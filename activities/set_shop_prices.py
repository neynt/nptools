from datetime import timedelta
import re

from lib import NeoPage
from lib import item_db

shop_item_re = re.compile(r'''</td></tr><tr><td width=60 bgcolor='#ffffcc'><b>(.*?)</b></td><td align=center width=80><img src='http://images\.neopets\.com/items/(.*?)' height=80 width=80></td><td width=50 bgcolor='#ffffcc' align=center><b>(\d+)</b></td><td bgcolor='#ffffcc'><b>(.*?)</b></td><input type='hidden'  name='(.*?)' value='(\d+)'><input type='hidden' name='(.*?)'  value='(\d+)'></td><td align=center bgcolor='#ffffcc'><input type='text' name='(.*?)' size='6' maxlength='6' value='\d+'></td><td width=180 bgcolor='#ffffcc'><i>(.*?)</i></td><td width=40 bgcolor='#ffffcc' align=center><select name=(.*?)>''')

def set_shop_prices():
    np = NeoPage()
    np.get('/market_your.phtml')
    args = []
    args.append('type=update_prices')
    args.append('order_by=')
    args.append('view=')
    results = shop_item_re.findall(np.content)
    orig_results = list(results)
    # TODO: figure out why this regex returns duplicates
    # and maybe sort it in a less terrible way
    results = list(set(results))
    results.sort(key=lambda x:next(i for i,v in enumerate(orig_results) if v[4] == x[4]))
    wiz_banned = False
    for (name, image, stock, category, obj_id_key, obj_id_val, old_cost_key,
            old_cost_val, cost_key, desc, back_to_inv_key) in results:
        old_cost_val = int(old_cost_val)
        args.append(f'{obj_id_key}={obj_id_val}')
        args.append(f'{old_cost_key}={old_cost_val}')
        my_price = 0
        try:
            true_price = item_db.get_price(name, image, update=not wiz_banned, max_laxness=5, max_age=timedelta(days=7))
            if true_price == None:
                pass
            elif type(true_price) == dict:
                print(f'Warning: {name} has multiple forms: {true_price}')
            elif true_price >= 1000000:
                print(f'Warning: {name} is unbuyable')
            else:
                my_price = true_price - 1
        except item_db.ShopWizardBannedException:
            wiz_banned = True
        if my_price == old_cost_val:
            print(f'Keeping {name} at {old_cost_val} NP')
        if my_price != old_cost_val:
            print(f'Will set {name} from {old_cost_val} to {my_price} NP')
        args.append(f'{cost_key}={my_price}')
        args.append(f'{back_to_inv_key}=0')
    args.append('obj_name=')
    print(args)
    np.post('/process_market.phtml', *args)

if __name__ == '__main__':
    set_shop_prices()
