# Here it is. The holy grail of Neopets automation -- restocking.
import bisect
import datetime
import io
import os
import re
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

import lib
from lib.data import backup_price_data
from lib import item_db
from lib import inventory
from lib import neotime

re_shop_item = re.compile(r'''<A href=".*?obj_info_id=(\d+)&stock_id=(\d+)&g=(\d+)" onClick=".*?brr=(\d+)';.*?"><IMG src="http://images.neopets.com/items/(.*?)" .*? title="(.*?)" border="1"><BR></A><B>(.*?)</B><BR>(\d+) in stock<BR>Cost: (.*?) NP''')
re_header = re.compile(r'''<td class="contentModuleHeader">(.*?)</td>''')
re_captcha = re.compile(r'''<input type="image" src="/captcha_show\.phtml\?_x_pwned=(.*?)".*>''')

MIN_PROFIT = 2000
MIN_PROFIT_MARGIN = 0.8

def find_neopet(img_data, img_name):
    img = Image.open(io.BytesIO(img_data))
    os.makedirs('shop_captchas', exist_ok=True)
    img.save(f'shop_captchas/{img_name}.png')
    filtered = img.filter(ImageFilter.FIND_EDGES)
    filtered.save(f'shop_captchas/{img_name}-filtered.png')
    width, height = img.size
    # Take median x and median y coordinate of N darkest pixels.
    # Impl is a bit slow, but at least conceptually clear
    N = 21
    best_score = -100000
    xys = []
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            r, g, b = img.getpixel((x, y))
            fr, fg, fb = filtered.getpixel((x, y))
            score = (fr + fg + fb) - (r + g + b)
            xys.append((score, (x, y)))
    xys.sort()
    xys = xys[-N:]
    best_x = sorted(x for _, (x, y) in xys)[N//2]
    best_y = sorted(y for _, (x, y) in xys)[N//2]
    draw = ImageDraw.Draw(img)
    draw.ellipse((best_x - 5, best_y - 5, best_x + 5, best_y + 5), fill=(255, 0, 0))
    for _, (x, y) in xys:
        draw.point((x, y), fill=(255, 255, 0))
    img.save(f'shop_captchas/{img_name}-solved.png')

    # introduce a bit of noise
    best_x += random.randint(-5, 5)
    best_y += random.randint(-5, 5)
    return best_x, best_y

def haggle_price(price):
    #price = int(price * 0.98)
    if price < 100:
        return price
    base = price
    while base >= 100: base //= 10
    base -= 1
    if base < 10: base = 98
    result = base
    while result < price:
        result = result * 10 + (result % 100 // 10)
    result //= 10
    return result

def restock(shop_id):
    inventory.ensure_np(99999)
    np = lib.NeoPage()
    np.get('/objects.phtml', f'obj_type={shop_id}', 'type=shop')
    items = re_shop_item.findall(np.content)
    shop_name = re_header.search(np.content)[1].strip()
    print(f'{len(items)} items found at {shop_name}.')

    # Look for profitable items
    best_score = ()
    best = None
    for obj_info_id, stock_id, g, brr, image, desc, name, stock, price in items:
        price = lib.amt(price)
        # TODO: Here we assume that items with the same name but drastically
        # different value won't restock in shops. For a more fine-grained
        # search, should search using image as well.
        true_price = item_db.get_price(name, update=False) or backup_price_data.get(name)
        if not true_price:
            continue
        #print(f'Item: {stock} x {name} for {price} NP. (True price {true_price} NP)')

        profit = true_price - price
        score = (profit, profit / price)
        if score > best_score:
            #print(f'{name}: {score}')
            best_score = score
            best = (name, price, obj_info_id, stock_id, brr)

    if not best:
        return

    name, price, obj_info_id, stock_id, brr = best
    profit, profit_margin = best_score
    if profit >= MIN_PROFIT and profit_margin >= MIN_PROFIT_MARGIN:
        print(f'Trying to buy {name} for {offer} !! (profit {profit_margin*100:.1f}% = {profit} NP)')
        np.get('/haggle.phtml', f'obj_info_id={obj_info_id}', f'stock_id={stock_id}', f'brr={brr}')
        referer = np.referer
        _x_pwned = re_captcha.search(np.content)[1]
        np.get('/captcha_show.phtml', f'_x_pwned={_x_pwned}')

        offer = haggle_price(price)
        print(f'Trying to buy {name} for {offer} !! (profit {profit_margin*100:.1f}% = {profit} NP)')
        best_x, best_y = find_neopet(np.content, _x_pwned)
        np.set_referer(referer)
        print(f'Haggling @ {offer}')

        np.post('/haggle.phtml', f'current_offer={offer}', f'x={best_x}', f'y={best_y}')
        if 'I accept your offer' in np.content:
            print('Bought !!!')
        else:
            print('Not bought :( TODO: See what happened')
    else:
        print(f'No worthy items found. Best was {name} (profit {profit_margin*100:.1f}% = {profit} NP)')

    # Learn about unknown items
    for obj_info_id, stock_id, g, brr, image, desc, name, stock, price in items:
        try:
            item_db.get_price(name)
        except item_db.ShopWizardBannedException:
            return

if __name__ == '__main__':
    #restock(13) # Neopian Pharmacy
    #restock(79) # Brightvale Glaziers
    restock(68) # Collectable Coins
    #restock(14) # Chocolate Factory
    #restock(58) # Post office
    #restock(8) # Collectable cards
    #gen_restock_list()
