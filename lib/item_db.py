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

level2_cache = {}

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
    lowest_price = UNBUYABLE_PRICE

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
            lowest_price = min(lowest_price, price)
        g = c2g[lib.strip_tags(rows[0][0])[0]]
        markets[obj_info_id][g] = market_data
        if search_count >= 30 * len(markets): break

        found = sum(len(md) for md in markets.values())
        total = len(markets) * (len(char_groups) - (laxness))
        print(f'\r({item_name}: {lowest_price} NP; {found}/{total}; {search_count}) ', end='')
    print()

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
                image, desc, name = res[1], res[2], res[3]
                print(f'{link} has {stock}')
                if cur_amt <= 2:
                    cur_price = price
                cur_amt += stock
                # The price of an item for our purposes is the price of the 2nd
                # cheapest item in the market.
                if cur_amt >= 2:
                    break
            else:
                # TODO: This probably actually means the item is unbuyable.
                print(f'Unable to find enough sellers for {obj_info_id}. Assuming unbuyable.')
                cur_price = UNBUYABLE_PRICE

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
        SELECT image FROM items WHERE name = ?
        ''', (item_name,))
        result = c.fetchone()

        if not result:
            c.execute('''
            INSERT INTO items (name, last_updated)
            VALUES (?, datetime('now'))
            ON CONFLICT (name, image)
            DO UPDATE SET last_updated=datetime('now')
            ''', (item_name,))

        c.execute('''
        UPDATE items SET price=?, price_laxness=?, price_last_updated=datetime('now') WHERE name=?
        ''', (1000001, laxness, item_name))

    conn.commit()

    level2_cache.update(level2_by_item)
    return level2_by_item

# Fetches the market for an item.
# i.e. (price, stock, link) tuples, cheapest first
def get_market(name, image=None):
    c = conn.cursor()
    if image:
        c.execute('''
        SELECT obj_info_id FROM items WHERE name = ? AND image = ?
        ''', (name, image))
    else:
        c.execute('''
        SELECT obj_info_id FROM items WHERE name = ? 
        ''', (name,))
    ids = c.fetchall()
    result = {}
    for obj_info_id, in ids:
        if obj_info_id not in level2_cache:
            update_prices(name, laxness=5)
        result[obj_info_id] = level2_cache[obj_info_id]
    if len(result) == 1:
        result = list(result.values())[0]
    return result

# Mostly Neohome Superstore items
fixed_prices = {
    'Blue Maraqua Wall Paint': 400,
    'Blue Meridell Wall Paint': 400,
    'Green Mystery Island Wall Paint': 400,
    'Yellow Neopia Central Wall Paint': 400,
    'Green Roo Island Wall Paint': 400,
    'Red Shenkuu Wall Paint': 400,
    'Blue Terror Mountain Wall Paint': 400,
    'Brown Tyrannia Wall Paint': 400,
    'Grey Virtupets Wall Paint': 400,
    'Yellow Altador Wall Paint': 400,
    'Yellow Brightvale Wall Paint': 400,
    'Purple Darigan Citadel Wall Paint': 400,
    'Pink Faerieland Wall Paint': 400,
    'Orange Haunted Woods Wall Paint': 400,
    'Green Kiko Lake Wall Paint': 400,
    'Red Krawk Island Wall Paint': 400,
    'Purple Kreludor Wall Paint': 400,
    'Golden Lost Desert Wall Paint': 400,
    'Pink Lutari Island Wall Paint': 400,

    'Simple Wood Floor': 500,
    'Basic Red Floor Tiles': 500,
    'Basic Peach Floor Tiles': 500,
    'Basic Orange Floor Tiles': 500,
    'Basic Buff Floor Tiles': 500,
    'Basic Yellow Floor Tiles': 500,
    'Basic Mint Green Floor Tiles': 500,
    'Basic Green Floor Tiles': 500,
    'Basic Teal Floor Tiles': 500,
    'Basic Blue Floor Tiles': 500,
    'Basic Violet Floor Tiles': 500,
    'Basic Purple Floor Tiles': 500,
    'Basic Black Floor Tiles': 483,
    'Basic White Floor Tiles': 400,

    'Simple Yellow Chair': 4122,
    'Simple Yellow Sofa': 1158,
    'Simple Blue Chair': 792,
    'Simple Purple Chair': 1101,
    'Simple Purple Sofa': 1794,
    'Simple Blue Sofa': 905,
    'Simple Green Chair': 999,
    'Simple Green Sofa': 3445,
    'Simple Red Chair': 1077,
    'Simple Red Sofa': 1915,

    'Simple Yellow Table': 2427,
    'Simple Blue Side Table': 1116,
    'Simple Purple Side Table': 1523,
    'Simple Purple Table': 786,
    'Simple Blue Table': 836,
    'Simple Green Side Table': 2174,
    'Simple Red Side Table': 723,
    'Simple Green Table': 739,
    'Simple Yellow Side Table': 857,
    'Simple Red Table': 1020,

    'Simple Yellow Bed': 1471,
    'Simple Purple Bed': 1242,
    'Simple Blue Bed': 742,
    'Simple Green Bed': 624,
    'Simple Red Bed': 1071,

    'Simple Blue Lamp': 1048,
    'Simple Purple Lamp': 451,
    'Simple Green Lamp': 992,
    'Simple Red Lamp': 1724,
    'Simple Yellow Lamp': 777,

    'Simple Blue Rug': 1966,
    'Simple Purple Rug': 460,
    'Simple Green Rug': 557,
    'Simple Red Rug': 1007,
    'Simple Yellow Rug': 2111,
}

# Fetches the price of an item.
# item_name: Name of the item.
# item_image: Image of the item. If None and there are multiple items with that
# name, returns a map from obj_info_id to price.
# update: Whether or not to update the price.
# laxness: Laxness with which to update the price (max number of shop wizard
# sections missed).
def get_price(item_name, item_image=None, update=True, max_laxness=7, max_age=timedelta(days=9999)):
    if item_name in fixed_prices:
        return fixed_prices[item_name]
    c = conn.cursor()
    if item_image:
        get_results = lambda: c.execute('''
        SELECT image, price, price_laxness, price_last_updated FROM items
        WHERE name = ? AND (image = ? OR image = 'NONE')
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
