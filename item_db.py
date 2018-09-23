# Neopets item database.
# Since this would be a singleton anyway, I made it a module instead of a full
# class (that we instantiate only one of).
import sqlite3

import lib
from lib import NeoPage

ITEM_DB_FILE = 'itemdb.db'
UNBUYABLE_PRICE = 1000001

conn = sqlite3.connect(ITEM_DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES)

def update_schema():
    # Really nice simple schema update scheme. None of that versioning
    # garbage. Simply copy over shared columns to a temp table and replace
    # the old table!
    c = conn.cursor()
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
    conn.commit()

def query(self, q, *args):
    c = conn.cursor()
    result = c.execute(q, args)
    conn.commit()
    return c

# Updates prices for items with a given name by repeatedly searching with the
# shop wizard. Identifies when there are multiple items with the same name and
# updates ALL of them. Returns a "level2" view of the market (i.e. order book
# of sells, cheapest first, with links) -- which can be useful if you want to
# buy something.
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
        print(f'\r({sum(len(md) for md in markets.values())}/{len(markets) * len(char_groups)}) ', end='')
        np.post('/market.phtml', *opts)
        tbl = np.search(r'<table width="600".*?>(.*?)</table>')
        if not tbl:
            if np.contains('Whoa there, too many'):
                print('Shop wizard banned.')
                return
            ub_count += 1
            if ub_count >= 5: break
            continue
        tbl = tbl[1]
        rows = table_to_tuples(tbl, raw=True)[1:]
        search_count += 1
        if search_count >= 50: break
        market_data = []
        obj_info_id = None
        for owner, item, stock, price in rows:
            result = re.search(r'<a href="(.*?)"><b>(.*?)</b></a>', owner)
            link = result[1]
            owner = result[2]
            result = re.search(r'/browseshop.phtml\?owner=(.*?)&buy_obj_info_id=(.*?)&buy_cost_neopoints=(\d+)', link)
            obj_info_id = int(result[2])
            price = lib.amt(lib.strip_tags(price))
            stock = lib.amt(stock)
            market_data.append((price, stock, link))
        g = c2g[lib.strip_tags(rows[0][0])[0]]
        markets[obj_info_id][g] = market_data

    level2_by_item = {}
    # Consolidate results for each item into a quote.
    for obj_info_id, market_data in markets.items():
        level2 = sorted(sum(market_data.values(), []))
        level2_by_item[obj_info_id] = level2
        # The price of an item for our purposes is the price of the nth
        # cheapest item in the market.
        cur_amt = 0
        cur_price = UNBUYABLE_PRICE
        for price, stock, link in level2:
            cur_price = price
            cur_amt += stock
            if cur_amt >= 5:
                break
        print(f'The price of {item_name} (id {obj_info_id}) is {cur_price} NP.')
        cur_amt = 0
        for price, stock, link in level2:
            cur_amt += stock
            if cur_amt >= 30:
                break

        c = conn.cursor()
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
                    print(f'{market_data[2]} is froze?')
                    continue
                image = res[1]
                desc = res[2]
                name = res[3]
                c.execute('''
                INSERT INTO items (name,image,desc,obj_info_id,last_updated)
                VALUES (?,?,?,?,datetime('now'))
                ON CONFLICT (name,image)
                DO UPDATE SET desc=?, obj_info_id=?, last_updated=datetime('now')
                ''', (name, image, desc, obj_info_id, desc, obj_info_id))
                break
            else:
                print('Unable to find legit seller for {obj_info_id}. Will not store it in itemdb.')
                continue
        c.execute('''
        UPDATE items SET price=?, price_last_updated=datetime('now') WHERE obj_info_id=?
        ''', (cur_price, obj_info_id))

    conn.commit()
    return level2_by_item

# Fetches the price of an item. Updates prices first if a price is not already
# stored in the db.
def get_price(item_name, item_image=None):
    c = conn.cursor()
    results = None
    if item_image:
        c.execute('''
        SELECT image, price FROM items
        WHERE name = ? AND image = ?
        ''', (item_name, item_image))
        results = c.fetchall()
    else:
        c.execute('''
        SELECT image, price FROM items
        WHERE name = ?
        ''', (item_name,))
        results = c.fetchall()
    if len(results) > 1:
        print(f'Warning: More than one item with name {item_name}.')
    ret = {}
    if not (results and all(price for image, price in results)):
        market = self.update_prices(item_name)
        print(market)
        return self.get_price(item_name, item_image=item_image)
    for image, price in results:
        ret[image] = price
    if len(ret) == 1:
        return list(ret.values())[0]
    else:
        return ret
