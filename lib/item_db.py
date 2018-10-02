# Neopets item database.
# Since this would be a singleton anyway, I made it a module instead of a full
# class (that we instantiate only one of).
from datetime import datetime, timedelta
from collections import defaultdict
import re
import sqlite3

import lib
from . import NeoPage

ITEM_DB_FILE = 'itemdb.db'
UNBUYABLE_PRICE = 1000001

conn = sqlite3.connect(ITEM_DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES)

last_ban = None

class ShopWizardBannedException(Exception):
    pass

def update_schema():
    # Really nice simple schema update scheme. None of that versioning
    # garbage. Simply copy over shared columns to a temp table and replace
    # the old table!
    c = conn.cursor()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS items (id integer primary key);
    DROP TABLE IF EXISTS new_items;
    CREATE TABLE new_items (
        id integer PRIMARY KEY,
        name text not null,
        image text not null default 'NONE',
        desc text,
        obj_info_id int,
        price real,
        liquidity int,
        last_updated timestamp,
        price_laxness int,
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

def query(q, *args):
    c = conn.cursor()
    result = c.execute(q, args)
    conn.commit()
    return c

# Updates prices for items with a given name by repeatedly searching with the
# shop wizard. Identifies when there are multiple items with the same name and
# updates ALL of them. Returns a "level2" view of the market (i.e. order book
# of sells, cheapest first, with links) -- which can be useful if you want to
# buy something.
def update_prices(item_name, laxness=5):
    global last_ban
    now = datetime.now()
    if last_ban and (now - last_ban < timedelta(minutes=1) or (now - last_ban < timedelta(hours=1) and now.hour == last_ban.hour)):
        print('Still wiz banned.')
        raise ShopWizardBannedException

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
        np.post('/market.phtml', *opts)
        if np.contains('Whoa there, too many'):
            print('Shop wizard banned.')
            last_ban = datetime.now()
            raise ShopWizardBannedException

        tbl = np.search(r'<table width="600".*?>(.*?)</table>')
        if not tbl:
            ub_count += 1
            if ub_count >= 15: break
            continue
        tbl = tbl[1]
        rows = lib.table_to_tuples(tbl, raw=True)[1:]
        search_count += 1
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
        if search_count >= 30 * len(markets): break
        print(f'\r({sum(len(md) for md in markets.values())}/{len(markets) * (len(char_groups) - (laxness))}; {search_count}) ', end='')

    level2_by_item = {}

    # Consolidate results for each item into a quote.
    if markets:
        for obj_info_id, market_data in markets.items():
            level2 = sorted(sum(market_data.values(), []))
            level2_by_item[obj_info_id] = level2

            cur_amt = 0
            cur_price = UNBUYABLE_PRICE
            image, desc, name = None, None, None

            for price, stock, link in level2:
                np.get(link)
                res = np.search(r'''<A href=".*?" onClick=".*?"><img src="http://images.neopets.com/items/(.*?)" .*? title="(.*?)" border="1"></a> <br> <b>(.*?)</b>''')
                if not res:
                    print(f'{link} is frozen?')
                    continue
                print(f'{link} is selling {name} for {price}')
                image, desc, name = res[1], res[2], res[3]
                if cur_amt <= 2:
                    cur_price = price
                cur_amt += stock
                # The price of an item for our purposes is the price of the 2nd
                # cheapest item in the market.
                if cur_amt >= 2:
                    break
            else:
                # TODO: This probably actually means the item is unbuyable.
                print('Unable to find legit seller for {obj_info_id}. Will not store it in itemdb.')
                continue

            print(f'The price of {item_name} (id {obj_info_id}) is {cur_price} NP.')

            c = conn.cursor()
            c.execute('''
            SELECT name FROM items WHERE obj_info_id=?
            ''', (obj_info_id,))
            result = c.fetchone()

            if not result or result[0][0] != item_name:
                c.execute('''
                INSERT INTO items (name, image, desc, obj_info_id, last_updated)
                VALUES (?, ?, ?, ?, datetime('now'))
                ON CONFLICT (name, image)
                DO UPDATE SET desc=?, obj_info_id=?, last_updated=datetime('now')
                ''', (name, image, desc, obj_info_id, desc, obj_info_id))

            c.execute('''
            UPDATE items SET price=?, price_laxness=?, price_last_updated=datetime('now') WHERE obj_info_id=?
            ''', (cur_price, laxness, obj_info_id))
    else:
        print(f'It seems {item_name} is unbuyable.')
        # Item could not be found; assume it's unbuyable.
        # We use a cheap price estimate of 1,000,001 NP.
        # TODO: Items inserted in this way will have a wonky image property.
        c = conn.cursor()
        c.execute('''
        INSERT INTO items (name, last_updated, price, price_laxness, price_last_updated)
        VALUES (?, datetime('now'), 1000001, ?, datetime('now'))
        ON CONFLICT (name, image)
        DO UPDATE SET last_updated=datetime('now'), price=1000001, price_laxness=?, price_last_updated=datetime('now')
        ''', (item_name, laxness, laxness))

    conn.commit()
    return level2_by_item

# Fetches the price of an item.
# item_name: Name of the item.
# item_image: Image of the item. If None and there are multiple items with that
# name, returns a map from obj_info_id to price.
# update: Whether or not to update the price.
# laxness: Laxness with which to update the price (max number of shop wizard
# sections missed).
def get_price(item_name, item_image=None, update=True, max_laxness=9, max_age=timedelta(days=9999)):
    c = conn.cursor()
    if item_image:
        get_results = lambda: c.execute('''
        SELECT image, price, price_laxness, price_last_updated FROM items
        WHERE name = ? AND (image = ? OR image = NULL)
        ''', (item_name, item_image))
        results = c.fetchall()
    else:
        get_results = lambda: c.execute('''
        SELECT image, price, price_laxness, price_last_updated FROM items
        WHERE name = ?
        ''', (item_name,))
        results = c.fetchall()
    for attempt_ in range(2):
        get_results()
        results = c.fetchall()
        if len(results) > 1:
            print(f'Warning: More than one item with name {item_name}.')

        good = len(results) > 0
        for image, price, laxness, last_updated in results:
            if not (
                laxness and
                price and
                int(laxness) <= max_laxness and
                datetime.utcnow() - last_updated <= max_age
            ):
                good = False

        if not good:
            if not update: return None
            market = update_prices(item_name, laxness=max_laxness)
            continue

        ret = {}
        for image, price, _, _ in results:
            ret[image] = int(price)
        if len(ret) == 1:
            return list(ret.values())[0]
        else:
            return ret
