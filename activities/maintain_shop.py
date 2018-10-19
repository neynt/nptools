from datetime import timedelta
import re

from lib import NeoPage
from lib import item_db
from lib import util
import lib.g as g

shop_item_re = re.compile(r'''</td></tr><tr><td width=60 bgcolor='#ffffcc'><b>(.*?)</b></td><td align=center width=80><img src='http://images\.neopets\.com/items/(.*?)' height=80 width=80></td><td width=50 bgcolor='#ffffcc' align=center><b>(\d+)</b></td><td bgcolor='#ffffcc'><b>(.*?)</b></td><input type='hidden'  name='(.*?)' value='(\d+)'><input type='hidden' name='(.*?)'  value='(\d+)'></td><td align=center bgcolor='#ffffcc'><input type='text' name='(.*?)' size='6' maxlength='6' value='\d+'></td><td width=180 bgcolor='#ffffcc'><i>(.*?)</i></td><td width=40 bgcolor='#ffffcc' align=center><select name=(.*?)>''')

def set_shop_prices():
    np = NeoPage()

    g.items_stocked.clear()
    lim = 30
    while True:
        np.get('/market.phtml', 'order_by=id', 'type=your', f'lim={lim}')
        has_next = "<input type='submit' name='subbynext' value='Next 30'>" in np.content
        args = []
        args.append('type=update_prices')
        args.append('order_by=')
        args.append('view=')
        results = shop_item_re.findall(np.content)
        for (name, image, stock, category, obj_id_key, obj_id_val, old_cost_key,
                old_price, cost_key, desc, back_to_inv_key) in results:
            stock = int(stock)
            old_price = int(old_price)
            obj_id_val = int(obj_id_val)
            args.append(f'{obj_id_key}={obj_id_val}')
            args.append(f'{old_cost_key}={old_price}')

            g.items_stocked[obj_id_val] = stock

            my_price = old_price
            try:
                true_price = item_db.get_price(name, image, max_laxness=3, max_age=timedelta(days=7))
                if true_price == None:
                    pass
                elif type(true_price) == dict:
                    print(f'Warning: {name} has multiple forms: {true_price}')
                elif true_price >= 1000000:
                    print(f'Warning: {name} is unbuyable')
                else:
                    my_price = true_price - 1
            except item_db.ShopWizardBannedException:
                pass
            if my_price != old_price:
                print(f'Setting {name} from {old_price} to {my_price} NP')
            args.append(f'{cost_key}={my_price}')
            args.append(f'{back_to_inv_key}=0')
        args.append('obj_name=')
        np.post('/process_market.phtml', *args)
        lim += 30
        if not has_next:
            break

SALES_LOG_FILE = 'shop_sales.log'

def clean_shop_till():
    log = open(SALES_LOG_FILE, 'a')
    np = NeoPage()

    np.get('/market.phtml', 'type=sales')
    referer = np.referer
    if 'Nobody has bought anything' in np.content:
        print('No new sales.')
    else:
        tbl = re.search('''<table align=center width=530 cellpadding=3 cellspacing=0>(.*?)</table>''', np.content)[1]
        rows = util.table_to_tuples(tbl)
        total_sales = 0
        for date, item, buyer, price in rows[1:-1]:
            price = util.amt(price)
            print(f'{date}: {buyer} bought {item} for {price} NP')
            log.write(f'{date},{buyer},{item},{price}\n')
            total_sales += price

        print(f'Total sales cleared: {total_sales} NP')
        print(f'Saved to {SALES_LOG_FILE}. Clearing history.')
        np.post('/market.phtml', 'type=sales', 'clearhistory=true')

    np.set_referer(referer)
    np.get('/market.phtml', 'type=till')
    amt = util.amt(re.search(r'''You currently have <b>(.*?)</b> in your till.''', np.content)[1])
    if amt:
        print(f'Withdrawing {amt} NP from shop till.')
        np.post('/process_market.phtml', 'type=withdraw', f'amount={amt}')
    else:
        print(f'Shop till is empty.')

if __name__ == '__main__':
    set_shop_prices()
    clean_shop_till()
