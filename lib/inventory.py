# Utilities for manipulating items and neopoints.
import re

from lib import NeoPage
from activities import bank_interest
from . import item_db

def list_items():
    np = NeoPage()
    np.get('/inventory.phtml')
    items = np.findall(r'\n<td class=.*?>.*?</td>')
    for item in items:
        attr = re.search(r'<td class="(.*?)"><a href="javascript:;" onclick="openwin\((\d+)\);"><img src="http://images.neopets.com/items/(.*?)" width="80" height="80" title="(.*?)" alt="(.*?)" border="0" class="(.*?)"></a><br>(.*?)(<hr noshade size="1" color="#DEDEDE"><span class="attr medText">(.*?)</span>)?</td>', item)
        item_id = attr[2]
        item_image = attr[3]
        item_desc = attr[4]
        item_name = attr[7]

        item_db.query('''
        INSERT INTO items (name,image,desc,last_updated)
        VALUES (?,?,?,datetime('now'))
        ON CONFLICT (name,image) DO UPDATE SET desc=?, last_updated=datetime('now')
        ''', item_name, item_image, item_desc, item_desc)

def deposit_all_items(exclude=[]):
    # First list items to add them to the item db
    np = NeoPage()
    list_items()
    np.get('/quickstock.phtml')
    items = np.findall(r'''<TD align="left">(.*?)</TD><INPUT type="hidden"  name="id_arr\[(.*?)\]" value="(\d+?)">''')
    args = []
    args.append('buyitem=0')
    for name, idx, item_id in items:
        args.append(f'id_arr[{idx}]={item_id}')
        if name not in exclude:
            args.append(f'radio_arr[{idx}]=deposit')
    np.post('/process_quickstock.phtml', *args)

def ensure_np(amount):
    # Withdraws from the bank to get up at least [amount] NP.
    np = NeoPage()
    np.get('/bank.phtml')
    if np.contains('Collect Interest ('):
        bank_interest.bank_interest()
    nps = np.search(r'''<a id='npanchor' href="/inventory.phtml">(.*?)</a>''')[1]
    nps = int(nps.replace(',', ''))
    if nps >= amount: return
    need = amount - nps
    denom = 10**max(len(str(need)), len(str(amount)))
    need = (need // denom + 1) * denom
    np.post('/process_bank.phtml', 'type=withdraw', f'amount={need}')
    print(f'Withdrawing {need} NP')
