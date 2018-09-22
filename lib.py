from collections import defaultdict
from datetime import datetime
import io
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

    def update_schema(self):
        # Really nice simple schema update scheme. None of that versioning
        # garbage. Simply copy over shared columns to a temp table and replace
        # the old table!
        c = self.conn.cursor()
        c.executescript('''
        CREATE TABLE IF NOT EXISTS items (id integer primary key);
        DROP TABLE IF EXISTS new_items;
        CREATE TABLE new_items (
            id integer primary key,
            name text not null,
            image text,
            desc text,
            obj_info_id int,
            price real,
            liquidity int,
            last_updated timestamp,
            price_last_updated timestamp,
            UNIQUE (name, image),
            UNIQUE (obj_info_id)
        );
        ''')
        c.execute('''
        PRAGMA table_info(items)
        ''')
        current_columns = [r[1] for r in c.fetchall()]
        c.execute('''
        PRAGMA table_info(new_items)
        ''')
        new_columns = [r[1] for r in c.fetchall()]
        ported_columns = ', '.join(c for c in current_columns if c in new_columns)
        print(f'Porting columns: {ported_columns}. All others will be lost.')
        c.executescript(f'''
        INSERT INTO new_items ({ported_columns}) SELECT {ported_columns} FROM items;
        DROP TABLE items;
        ALTER TABLE new_items RENAME TO items;
        ''')
        self.conn.commit()

    def query(self, q, *args):
        c = self.conn.cursor()
        result = c.execute(q, args)
        self.conn.commit()
        return result

    def update_prices(self, item_name, laxness=3):
        char_groups = 'an0 bo1 cp2 dq3 er4 fs5 gt6 hu7 iv8 jw9 kx_ ly mz'.split()
        c2g = dict(sum(([(c, i) for c in cs] for i, cs in enumerate(char_groups)), []))
        markets = defaultdict(dict)
        ub_count = 0
        search_count = 0

        np = NeoPage('/market.phtml?type=wizard')
        opts = []
        opts.append('type=process_wizard')
        opts.append('feedset=0')
        opts.append(f'shopwizard={item_name}')
        opts.append('table=shop')
        opts.append('criteria=exact')
        opts.append('min_price=0')
        opts.append('max_price=999999')

        # Repeatedly search the shop wizard, collecting all results seen.
        while not markets or any(len(market_data) < len(char_groups) - laxness for market_data in markets.values()):
            print(f'{sum(len(md) for md in markets.values())}/{len(markets) * len(char_groups)}')
            np.post('/market.phtml', *opts)
            tbl = np.search(r'<table width="600".*?>(.*?)</table>')[1]
            rows = table_to_tuples(tbl, raw=True)[1:]
            search_count += 1
            if search_count >= 50: break
            if not rows:
                ub_count += 1
                if ub_count >= 5: break
                continue
            market_data = []
            obj_info_id = None
            for owner, item, stock, price in rows:
                result = re.search(r'<a href="(.*?)"><b>(.*?)</b></a>', owner)
                link = result[1]
                owner = result[2]
                result = re.search(r'/browseshop.phtml\?owner=(.*?)&buy_obj_info_id=(.*?)&buy_cost_neopoints=(\d+)', link)
                obj_info_id = int(result[2])
                price = amt(strip_tags(price))
                stock = amt(stock)
                market_data.append((price, stock, link))
            g = c2g[strip_tags(rows[0][0])[0]]
            markets[obj_info_id][g] = market_data

        # Consolidate results for each item into a quote.
        for obj_info_id, market_data in markets.items():
            level2 = sorted(sum(market_data.values(), []))
            # The price of an item for our purposes is the price of the nth
            # cheapest item in the market.
            cur_amt = 0
            cur_price = 1000001
            for price, stock, link in level2:
                cur_price = price
                cur_amt += stock
                if cur_amt >= 5:
                    break
            print(f'The price of {item_name} (id {obj_info_id}) is {cur_price} NP.')
            print(f'It can be bought at:')
            cur_amt = 0
            for price, stock, link in level2:
                print(f'{price} NP ({stock}): http://www.neopets.com{link}')
                cur_amt += stock
                if cur_amt >= 30:
                    break

            c = self.conn.cursor()
            c.execute('''
            SELECT image FROM items WHERE obj_info_id=?
            ''', (obj_info_id,))
            result = c.fetchone()
            if not result:
                for market_data in level2:
                    # Visit the shop and populate a bunch of fields
                    np.get(market_data[2])
                    res = np.search(r'''<A href=".*?" onClick=".*?"><img src="http://images.neopets.com/items/(.*?)" .*? title="(.*?)" border="1"></a> <br> <b>(.*?)</b>''')
                    if not res:
                        print('{market_data[2]} is froze?')
                        continue
                    image = res[1]
                    desc = res[2]
                    name = res[3]
                    c.execute('''
                    INSERT INTO items (name,image,desc,obj_info_id,last_updated)
                    VALUES (?,?,?,?,datetime('now'))
                    ON CONFLICT (name,image) DO UPDATE SET desc=?, obj_info_id=?, last_updated=datetime('now')
                    ''', (name, image, desc, obj_info_id, desc, obj_info_id))
                    break
                else:
                    print('Unable to find legit seller for {obj_info_id}. Will not store it in itemdb.')
                    continue
            c.execute('''
            UPDATE items SET price=?, price_last_updated=datetime('now') WHERE obj_info_id=?
            ''', (cur_price, obj_info_id))
        self.conn.commit()
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
#item_db.update_schema()

class Inventory:
    def list_items(self):
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

    def deposit_all_items(self, exclude=[]):
        # First list items to add them to the item db
        np = NeoPage()
        self.list_items()
        np.get('/quickstock.phtml')
        items = np.findall(r'''<TD align="left">(.*?)</TD><INPUT type="hidden"  name="id_arr\[(.*?)\]" value="(\d+?)">''')
        args = []
        args.append('buyitem=0')
        for name, idx, item_id in items:
            args.append(f'id_arr[{idx}]={item_id}')
            if name not in exclude:
                args.append(f'radio_arr[{idx}]=deposit')
        np.post('/process_quickstock.phtml', *args)

    def ensure_np(self, amount):
        # Withdraws from the bank to get up at least [amount] NP.
        np = NeoPage()
        np.get('/bank.phtml')
        nps = np.search(r'''<a id='npanchor' href="/inventory.phtml">(.*?)</a>''')[1]
        nps = int(nps.replace(',', ''))
        if nps >= amount: return
        need = amount - nps
        # Round up to next small multiple of power of ten
        need = 10**(len(str(need)) - 1) * (int(str(need)[0]) + 1)
        np.post('/process_bank.phtml', 'type=withdraw', f'amount={need}')
        print(f'Withdrawing {need} NP')

inv = Inventory()
