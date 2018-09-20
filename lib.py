import io
from datetime import datetime
import os
import pycurl
import re
import sqlite3
import time

def strip_tags(text):
    return ' '.join([t.strip() for t in re.split(r'<.*?>', text) if t.strip()])

def amt(x):
    return int(strip_tags(x).split()[0].replace(',', ''))

def dict_to_eq_pairs(kwargs):
    return [f'{k}={v}' for k, v in kwargs.items()]

def table_to_tuples(tbl, raw=False):
    result = []
    trs = re.findall(r'<tr.*?>(.*?)</tr>', tbl, flags=re.DOTALL)
    for i,tr in enumerate(trs):
        tds = re.findall(r'<td.*?>(.*?)</td>', tr, flags=re.DOTALL)
        tds = tuple(tds) if raw else tuple(map(strip_tags, tds))
        result.append(tds)
    return result

class NotLoggedInError(Exception):
    pass

class NeoPage:
    def __init__(self, path=None, user_agent='Mozilla/5.0'):
        self.storage = io.BytesIO()
        self.content = ''
        self.last_file_path = ''
        self.base_url = 'http://www.neopets.com'
        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.WRITEFUNCTION, self.storage.write)
        self.curl.setopt(pycurl.COOKIEFILE, 'nptools.cookies')
        self.curl.setopt(pycurl.COOKIEJAR, 'nptools.cookies')
        self.curl.setopt(pycurl.USERAGENT, user_agent)
        if path:
            self.get(path)

    def save_to_file(self, filename):
        open(filename, 'w').write(self.content)

    def load_file(self, filename):
        self.content = open(filename, 'r').read()

    def perform(self, url):
        self.curl.setopt(pycurl.URL, url)
        self.storage.seek(0)
        self.storage.truncate(0)
        self.curl.perform()
        self.content = self.storage.getvalue().decode('utf-8')
        self.curl.setopt(pycurl.REFERER, url)
        if 'templateLoginPopupIntercept' in self.content:
            print('Warning: Not logged in?')
        if 'randomEventDiv' in self.content:
            event = self.search(r'<div class="copy">(.*?)\t</div>')
            if event:
                event = strip_tags(event[1])
                print(f'[Random event: {event}]')
            else:
                print('[Random event]')

    def get_base(self, url, *params, **kwargs):
        if params or kwargs:
            url += '&' if '?' in url else '?'
            url += '&'.join(list(params) + dict_to_eq_pairs(kwargs))
        self.curl.setopt(pycurl.POST, 0)
        self.perform(url)

    def save_page(self, url, tag):
        parts = [x for x in url.split('/') if x]
        if not parts: parts = ['_']
        path_parts, filename = parts[:-1], parts[-1]
        path = '/'.join(['pages'] + path_parts)
        os.makedirs(path, exist_ok=True)
        time_ms = int(time.time() * 1000)
        self.last_file_path = f'{path}/{filename}_{tag}@{time_ms}'
        self.save_to_file(self.last_file_path)

    def get_url(self, url, *params, **kwargs):
        self.get_base(url, *params, **kwargs)
        self.save_page(url, 'get_url')

    def get(self, path, *params, **kwargs):
        self.get_base(self.base_url + path, *params, **kwargs)
        self.save_page(path, 'get')

    def post_base(self, url, *params, **kwargs):
        postfields = '&'.join(list(params) + dict_to_eq_pairs(kwargs))
        self.curl.setopt(pycurl.POST, 1)
        self.curl.setopt(pycurl.POSTFIELDS, postfields)
        self.perform(url)

    def post_url(self, url, *params, **kwargs):
        self.post_base(url, *params, **kwargs)
        self.save_page(url, 'post_url')

    def post(self, path, *params, **kwargs):
        self.post_base(self.base_url + path, *params, **kwargs)
        self.save_page(path, 'post')

    def find(self, *strings):
        loc = 0
        for string in strings:
            loc = self.content.find(string, loc)
        return loc

    def contains(self, string):
        return self.find(string) >= 0
    
    def search(self, regex):
        r = re.compile(regex, re.DOTALL)
        result = r.search(self.content)
        if not result:
            print(f'Warning: Search {regex} failed for page {self.last_file_path}')
        return result
    
    def findall(self, regex):
        r = re.compile(regex, re.DOTALL)
        return r.findall(self.content)
    
    def set_referer_path(self, path):
        self.curl.setopt(pycurl.REFERER, self.base_url + path)

    def set_referer(self, url):
        self.curl.setopt(pycurl.REFERER, url)
    
    def login(self, user, pwd):
        self.post('/login.phtml', f'username={user}&password={pwd}')

class ItemDb:
    def __init__(self, filename):
        self.conn = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES)

    def init_schema(self):
        c = self.conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id integer primary key,
            name text not null,
            image text,
            desc text,
            price real,
            liquidity int,
            last_updated timestamp,
            price_last_updated timestamp,
            UNIQUE (name, image)
        )
        ''')
        self.conn.commit()

    def query(self, q, *args):
        c = self.conn.cursor()
        result = c.execute(q, args)
        self.conn.commit()
        return result

    def update_prices(self, item_name):
        char_groups = 'an0 bo1 cp2 dq3 er4 fs5 gt6 hu7 iv8 jw9 kx_ ly mz'.split()
        c2g = dict(sum(([(c, i) for c in cs] for i, cs in enumerate(char_groups)), []))
        markets = {}

        np = NeoPage('/market.phtml?type=wizard')
        opts = []
        opts.append('type=process_wizard')
        opts.append('feedset=0')
        opts.append(f'shopwizard={item_name}')
        opts.append('table=shop')
        opts.append('criteria=exact')
        opts.append('min_price=0')
        opts.append('max_price=999999')
        #while len(markets) < len(char_groups):
        while len(markets) < 2:
            print(f'{len(markets)}/{len(char_groups)}')
            np.post('/market.phtml', *opts)
            tbl = np.search(r'<table width="600".*?>(.*?)</table>')[1]
            rows = table_to_tuples(tbl, raw=True)[1:]
            g = c2g[rows[0][0][0]]
            market_data = []
            for owner, item, stock, price in rows:
                result = re.search(r'<a href="(.*?)"><b>(.*?)</b></a>', owner)
                link = result[1]
                owner = result[2]
                result = re.search(r'href="/browseshop.phtml?owner=(.*?)&buy_obj_info_id=(.*?)&buy_cost_neopoints=(.*?)"', link)
                obj_info_id = result[2]
                market_data.append((price, owner, link, obj_info_id))
            markets[g] = rows

        return markets
    
    def get_price(self, item_name, item_image=None):
        c = self.conn.cursor()
        results = None
        if item_image:
            c.execute('''
            SELECT image, price FROM items
            WHERE name = ?
            ''', (item_name,))
            results = c.fetchall()
        else:
            c.execute('''
            SELECT image, price FROM items
            WHERE name = ? AND image = ?
            ''', (item_name, item_image))
            results = c.fetchall()
        if len(results) > 1:
            print(f'Warning: More than one item with name {item_name}.')
        ret = {}
        if not all(price for image, price in results):
            self.update_prices(item_name)
            return self.get_price(item_name, item_image=item_image)
        for image, price in results:
            ret[image] = price

item_db = ItemDb('itemdb.db')
item_db.init_schema()

class Inventory:
    def __init__(self, np=None):
        if not np:
            np = NeoPage()
        self.np = np

    def list_items(self):
        self.np.get('/inventory.phtml')
        items = self.np.findall(r'\n<td class=.*?>.*?</td>')
        for item in items:
            attr = re.search(r'<td class="(.*?)"><a href="javascript:;" onclick="openwin\((\d+)\);"><img src="http://images.neopets.com/items/(.*?)" width="80" height="80" title="(.*?)" alt="(.*?)" border="0" class="(.*?)"></a><br>(.*?)(<hr noshade size="1" color="#DEDEDE"><span class="attr medText">(.*?)</span>)?</td>', item)
            item_id = attr[2]
            item_image = attr[3]
            item_desc = attr[4]
            item_name = attr[7]

            item_db.query('''
            INSERT INTO items (name,image,desc,last_updated)
            VALUES (?,?,?,?)
            ON CONFLICT (name,image) DO UPDATE SET desc=?, last_updated=?
            ''', item_name, item_image,
            item_desc, datetime.now(),
            item_desc, datetime.now())

    def deposit_all_items(self, exclude=[]):
        # First list items to add them to the item db
        self.list_items()
        self.np.get('/quickstock.phtml')
        items = self.np.findall(r'''<TD align="left">(.*?)</TD><INPUT type="hidden"  name="id_arr\[(.*?)\]" value="(\d+?)">''')
        args = []
        args.append('buyitem=0')
        for name, idx, item_id in items:
            args.append(f'id_arr[{idx}]={item_id}')
            if name not in exclude:
                args.append(f'radio_arr[{idx}]=deposit')
        self.np.post('/process_quickstock.phtml', *args)

    def ensure_np(self, amount):
        # Withdraws from the bank to get up at least [amount] NP.
        self.np.get('/bank.phtml')
        nps = self.np.search(r'''<a id='npanchor' href="/inventory.phtml">(.*?)</a>''')[1]
        nps = int(nps.replace(',', ''))
        if nps >= amount: return
        need = amount - nps
        # Round up to next small multiple of power of ten
        need = 10**(len(str(need)) - 1) * (int(str(need)[0]) + 1)
        self.np.post('/process_bank.phtml', 'type=withdraw', f'amount={need}')
        print(f'Withdrawing {need} NP')

inv = Inventory()
