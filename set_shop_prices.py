import re

import lib
import item_db

shop_item_re = re.compile(r'''</tr><tr><td .*?><b>(.*?)</b></td><td .*?><img src='http://images\.neopets\.com/items/(.*?)' .*?></td><td .*?><b>(\d+)</b></td><td .*?><b>(.*?)</b></td><input type='hidden'.*?name='(.*?)' value='(.*?)'><input type='hidden' name='(.*?)'.*?value='(.*?)'></td><td .*?><input type='text' name='(.*?)'.*?></td><td .*?><i>(.*?)</i></td><td .*?><select name=(.*?)>''', flags=re.DOTALL)

def set_shop_prices():
    np = lib.NeoPage()
    np.get('/market_your.phtml')
    args = []
    args.append('type=update_prices')
    args.append('order_by=')
    args.append('view=')
    results = shop_item_re.findall(np.content)
    for (name, image, stock, category, obj_id_key, obj_id_val, old_cost_key,
            old_cost_val, cost_key, desc, back_to_inv_key) in results:
        args.append(f'{obj_id_key}={obj_id_val}')
        args.append(f'{old_cost_key}={old_cost_val}')
        try:
            true_price = item_db.get_price(name, image)
            if true_price < 1000000:
                my_price = true_price - 1
            else:
                my_price = 0
        except item_db.ShopWizardBannedException:
            my_price = 0
        if my_price != int(old_cost_val):
            print(f'Setting {name} to {my_price} NP')
        args.append(f'{cost_key}={my_price}')
        args.append(f'{back_to_inv_key}=0')
    args.append('obj_name=')
    np.post('/process_market.phtml', *args)

if __name__ == '__main__':
    set_shop_prices()
