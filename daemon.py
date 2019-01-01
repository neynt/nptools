# Plays Neopets in the background for you.

import atexit
import datetime
import logging
import os
import pickle
import pycurl
import random
import sys
import time
import itertools

from activities.anchor_management import anchor_management
from activities.apple_bobbing import apple_bobbing
from activities.bank_interest import bank_interest
from activities.battledome import battledome
from activities.cheeseroller import cheeseroller
from activities.coconut_shy import coconut_shy
from activities.council_chamber import council_chamber
from activities.deserted_tomb import deserted_tomb
from activities.faerie_caverns import faerie_caverns
from activities.fishing import fishing
from activities.forgotten_shore import forgotten_shore
from activities.fruit_machine import fruit_machine
from activities.grumpy_king import grumpy_king
from activities.healing_springs import healing_springs
from activities.jelly import jelly
from activities.kacheek_seek import kacheek_seek
from activities.kiko_pop import kiko_pop
from activities.lunar_temple import lunar_temple
from activities.magma_pool import magma_pool
from activities.omelette import omelette
import activities.training as training
from activities.food_club import food_club
from activities.plushie import plushie
from activities.plushie_tycoon import plushie_tycoon
from activities.pyramids import pyramids
from activities.restock import restock
from activities.rich_slorg import rich_slorg
from activities.scratchcard import buy_scratchcard
from activities.shrine import shrine
from activities.snowager import snowager
from activities.stock_market import stock_market
from activities.tombola import tombola
from activities.trudys_surprise import trudys_surprise
from activities.tyranu_evavu import tyranu_evavu
from activities.wise_king import wise_king
from activities.maintain_shop import set_shop_prices, clean_shop_till
from activities.faerieland_jobs import faerieland_jobs
from activities.lab_ray import lab_ray
from activities.lottery import lottery
from activities.fetch import fetch
from activities.expellibox import expellibox
from activities.shapeshifter import shapeshifter_daily

import lib
from lib import neotime
from lib.neotime import daily, now_nst
from lib import inventory
from lib import item_db
import lib.g as g

def appraise_items():
    # Identifies the price of items that we know about, but not the price of.
    while True:
        items = item_db.query('SELECT name FROM items WHERE price IS NULL').fetchall()
        items = sum((list(x) for x in items), [])
        if items:
            item = random.choice(items)
            print(f'Appraising {item} ({len(items)} items left)')
            try:
                item_db.update_prices(item, laxness=4)
            except item_db.ShopWizardBannedException:
                return
        else:
            return

# SS2: 13 (pharmacy), 41 (furniture), 108 (mystical surroundings)
restock_shops = [
    1, # Food
    2, # Magic
    3, # Toys
    (4, 15000), # Uni's clothing
    5, # Grooming parlour
    7, # Magical books
    8, # Collectable cards
    9, # Neopian petpets
    10, # Defense magic
    14, # Chocolate factory
    15, # Bakery
    16, # Health foods
    30, # Spooky food
    37, # Super Happy Icy Fun Snow Shop
    38, # Faerie books
    51, # Sutek's scrolls
    58, # Post office
    68, # Collectable coins
    70, # Booktastic books
    86, # Sea shells
    98, # Plushie palace
]

def next_restocks_f():
    while True:
        shops = random.sample(restock_shops, 10)
        shops1 = shops[:5]
        shops2 = shops[5:]
        for i in range(random.randint(2, 7)):
            yield shops1 if i % 2 == 0 else shops2
            if g.consec_empty_shops >= 5:
                break

next_restocks = next_restocks_f()

def my_restock():
    times = []
    for shop in next(next_restocks):
        if type(shop) == tuple:
            shop, min_profit = shop
            res = restock(shop, min_profit=min_profit)
        else:
            res = restock(shop)
        times.append(res or neotime.now_nst())
        time.sleep(0.5)
    result = max(times)
    result += datetime.timedelta(seconds=random.randint(30, 90))

    # Soft backoff
    if g.consec_empty_shops >= 40:
        print("Looks like we're restock banned. Backing off for 3 hours.")
        g.consec_empty_shops = 30
        result += datetime.timedelta(hours=3)
    elif g.consec_empty_shops >= 30:
        result += datetime.timedelta(minutes=5)
    elif g.consec_empty_shops >= 20:
        result += datetime.timedelta(minutes=2)
    elif g.consec_empty_shops >= 10:
        result += datetime.timedelta(minutes=1)
    return result

def clean_inventory():
    inventory.quickstock(exclude=['Pant Devil Attractor'])

def save_state():
    print('Saving global state to g.pickle')
    g.save_data()

# List[Tuple[String, Callable[[], None], Callable[[datetime], Optional[datetime]]]]
tasks = [
    # Dailies
    ('anchor_management', anchor_management, daily(1)),
    ('apple_bobbing', apple_bobbing, daily(1)),
    ('bank_interest', bank_interest, daily(0)),
    ('council_chamber', council_chamber, daily(1)),
    ('deserted_tomb', deserted_tomb, daily(1)),
    ('faerie_caverns', faerie_caverns, daily(1)),
    ('forgotten_shore', forgotten_shore, daily(1)),
    ('fruit_machine', fruit_machine, daily(1)),
    ('grumpy_king', grumpy_king, neotime.skip_lunch(daily(1))),
    ('jelly', jelly, daily(1)),
    ('kiko_pop', kiko_pop, daily(1)),
    ('lunar_temple', lunar_temple, daily(1)),
    ('omelette', omelette, daily(1)),
    ('plushie', plushie, daily(1)),
    ('rich_slorg', rich_slorg, daily(1)),
    ('stock_market', stock_market, daily(1)),
    ('tombola', tombola, daily(1)),
    ('coconut_shy', coconut_shy, daily(1)),
    ('trudys_surprise', trudys_surprise, daily(1)),
    ('lab_ray', lab_ray, daily(1)),
    ('lottery', lottery, daily(1)),
    ('wise_king', wise_king, neotime.skip_lunch(daily(1))),
    ('food_club', food_club, neotime.next_day_at(hour=12, minute=0, second=0)),

    # Longer-running dailies that we do after normal dailies
    ('battledome', battledome, daily(2)),
    #('shapeshifter', shapeshifter_daily, daily(2)),
    #('kacheek_seek', kacheek_seek, daily(2)),
    #('pyramids', pyramids, neotime.immediate),
    #('faerieland_jobs_1', lambda: faerieland_jobs(3), daily(2)),
    # TODO: Do 2 more jobs after first 3.

    # Multi-dailies
    ('buy_scratchcard', buy_scratchcard, neotime.after(hours=2, minutes=1)),
    #('buy_scratchcard', buy_scratchcard, neotime.after(hours=1, minutes=1)), # For boon
    ('fishing', fishing, neotime.after(hours=2)),
    ('healing_springs', healing_springs, neotime.after(minutes=95)),
    ('shrine', shrine, neotime.after(hours=13)),
    ('snowager', snowager, neotime.next_snowager_time),
    ('expellibox', expellibox, neotime.after(hours=8, minutes=1)),

    # Housekeeping
    #('plushie_tycoon', plushie_tycoon, neotime.after(minutes=15)),
    ('appraise_items', appraise_items, neotime.next_hour_at(minute=50, second=0)),
    #('pirate_academy', training.pirate_academy, neotime.immediate),
    ('island_training', training.island_training, neotime.immediate),
    ('clean inventory', clean_inventory, neotime.next_hour_at(minute=30, second=0)),

    # ooh oooh ooh oooo you gotta get cho money
    ('clean_shop_till', clean_shop_till, daily(1)),
    ('restock', my_restock, neotime.immediate),
    # TODO: shop wizard ban detect and retry
    ('set_shop_prices', set_shop_prices, neotime.next_hour_at(minute=40, second=0)),
    #('fetch', lambda: fetch(verbose=False) and None or None, neotime.after(minutes=5)),
    
    # Other
    #('magma_pool', magma_pool, neotime.after(minutes=4)),

    # Saving state
    ('save_state', save_state, neotime.after(minutes=15)),
]

# Prints seconds as "1d12h34m56.7s"
def pprint_seconds(secs):
    days = round(secs // (60*60*24))
    secs -= days * (60*60*24)
    hrs = round(secs // (60*60))
    secs -= hrs * (60*60)
    mins = round(secs // 60)
    secs -= mins * 60
    if days != 0:
        return f'{days}d{hrs}h{mins}m{secs:.0f}s'
    elif hrs != 0:
        return f'{hrs}h{mins}m{secs:.1f}s'
    elif mins != 0:
        return f'{mins}m{secs:.1f}s'
    else:
        return f'{secs:.2f}s'

def ensure_login():
    np = lib.NeoPage()
    np.get('/')
    if 'templateLoginPopupIntercept' in np.content:
        user = os.environ.get('NP_USER')
        pswd = os.environ.get('NP_PASS')
        np.login(user, pswd)
        if 'templateLoginPopupIntercept' in np.content:
            print('Failed to log in!')
            sys.exit(1)
        else:
            print('Logged in.')

def main():
    g.load_data()
    atexit.register(save_state)

    for name, f, _next_time in tasks:
        if name not in g.last_done:
            ensure_login()
            print(f'Never did {name} before. Doing.')
            f()
            g.last_done[name] = now_nst()

    find_next_task = lambda t: t[2](g.last_done[t[0]])
    failures = []
    while True:
        try:
            while True:
                now = now_nst()
                name, f, next_time = min(tasks, key=find_next_task)
                nxt = next_time(g.last_done[name])
                #print(f'{name}: Last done {g.last_done[name]}, next is {nxt}')
                time_til = (nxt - now).total_seconds()
                if time_til > 0:
                    print(f'[{now}: Doing {name} in {pprint_seconds(time_til)}]')
                    while True:
                        now = now_nst()
                        time_til = (nxt - now).total_seconds()
                        if time_til <= 0: break
                        time.sleep(min(60, time_til))
                else:
                    print(f'[{now}: Doing {name}]')
                ensure_login()
                # This allows individual functions to override the "time at
                # which the thing was done". For example, this is used to make
                # sure we only do the Snowager once every time it wakes up.
                g.last_done[name] = f() or now_nst()
        except lib.neo_page.NotLoggedInError:
            print('Unable to log in.')
        except KeyboardInterrupt:
            print('\nShutting down as requested.')
            break
        except pycurl.error as e:
            print('pycurl error: ', e)
            time.sleep(1)
        except Exception as e:
            logging.exception('')
            failures.append(e)
            if len(failures) > 10:
                print('Failures:')
                print(e)
                print('Too many failures; exiting.')
                break

if __name__ == '__main__':
    main()
