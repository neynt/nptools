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

from anchor_management import anchor_management
from apple_bobbing import apple_bobbing
from bank_interest import bank_interest
from battledome import battledome
from cheeseroller import cheeseroller
from coconut_shy import coconut_shy
from council_chamber import council_chamber
from deserted_tomb import deserted_tomb
from faerie_caverns import faerie_caverns
from fishing import fishing
from forgotten_shore import forgotten_shore
from fruit_machine import fruit_machine
from grumpy_king import grumpy_king
from healing_springs import healing_springs
from jelly import jelly
from kacheek_seek import kacheek_seek
from kiko_pop import kiko_pop
from lunar_temple import lunar_temple
from magma_pool import magma_pool
from omelette import omelette
from pirate_academy import pirate_academy
from plushie import plushie
from plushie_tycoon import plushie_tycoon
from pyramids import pyramids
from restock import restock
from rich_slorg import rich_slorg
from scratchcard import buy_scratchcard
from shrine import shrine
from snowager import snowager
from stock_market import stock_market
from tombola import tombola
from trudys_surprise import trudys_surprise
from tyranu_evavu import tyranu_evavu
from wise_king import wise_king

from neotime import daily, now_nst
import inventory
import item_db
import lib
import neotime

def appraise_item():
    # Identifies the price of an item that we know about, but not the price of.
    items = item_db.query('SELECT name FROM items WHERE price IS NULL').fetchall()
    items = sum((list(x) for x in items), [])
    if items:
        item = random.choice(items)
        print(f'Learning about {item}')
        try:
            item_db.update_prices(item, laxness=5)
        except item_db.ShopWizardBannedException:
            return neotime.now_nst() + datetime.timedelta(minutes=20)

def my_restock():
    stores = [
        1, # Food!
        68, # Collectable coins
        #38, # Faerie books
        #86, # Sea shells
        #14, # Chocolate factory
        #58, # Post office
        #8, # Collectible cards
    ]
    result = restock(random.choice(stores)) or neotime.now_nst()
    if result:
        result = result + datetime.timedelta(seconds=random.randint(0, 30))
    return result

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
    ('tombola', tombola, daily(1)),
    ('trudys_surprise', trudys_surprise, daily(1)),
    ('wise_king', wise_king, neotime.skip_lunch(daily(1))),

    # Longer-running dailies that we do after normal dailies
    ('stock_market', stock_market, daily(15)),
    ('battledome', battledome, daily(30)),
    ('kacheek_seek', kacheek_seek, daily(30)),
    ('pyramids', lambda:pyramids(True), daily(30)),

    # Multi-dailies
    ('buy_scratchcard', buy_scratchcard, neotime.after(hours=2, minutes=1)),
    ('fishing', fishing, neotime.after(hours=2)),
    ('healing_springs', healing_springs, neotime.after(minutes=35)),
    ('shrine', shrine, neotime.after(hours=12, minutes=1)),
    ('snowager', snowager, neotime.next_snowager_time),

    # Housekeeping
    ('clean inventory', lambda:inventory.deposit_all_items(exclude=['Five Dubloon Coin', 'Pant Devil Attractor']), neotime.after(hours=5)),
    ('plushie_tycoon', plushie_tycoon, neotime.after(minutes=15)),
    ('appraise_item', appraise_item, neotime.after(minutes=15)),
    ('pirate_academy', pirate_academy, neotime.immediate),

    # ooh oooh ooh oooo you gotta get cho money
    ('restock', my_restock, neotime.after(seconds=30)),
    
    # Other
    #('magma_pool', magma_pool, neotime.after(minutes=4)),
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
    # State
    last_done = {}

    PICKLE_FILE = 'daemon.pickle'

    if os.path.isfile(PICKLE_FILE):
        last_done = pickle.load(open(PICKLE_FILE, 'rb'))

    @atexit.register
    def save_data():
        print('Saving data...')
        pickle.dump(last_done, open(PICKLE_FILE, 'wb'))

    for name, f, _next_time in tasks:
        if name not in last_done:
            ensure_login()
            print(f'Never did {name} before. Doing.')
            f()
            last_done[name] = now_nst()

    find_next_task = lambda t: t[2](last_done[t[0]])
    failures = []
    while True:
        try:
            while True:
                now = now_nst()
                name, f, next_time = min(tasks, key=find_next_task)
                nxt = next_time(last_done[name])
                #print(f'{name}: Last done {last_done[name]}, next is {nxt}')
                time_til = (nxt - now).total_seconds()
                if time_til > 0:
                    print(f'[Doing {name} in {pprint_seconds(time_til)}]')
                    while True:
                        now = now_nst()
                        time_til = (nxt - now).total_seconds()
                        if time_til <= 0: break
                        time.sleep(min(60, time_til))
                else:
                    print(f'[Doing {name}]')
                ensure_login()
                # This allows individual functions to override the "time at
                # which the thing was done". For example, this is used to make
                # sure we only do the Snowager once every time it wakes up.
                last_done[name] = f() or now_nst()
        except lib.NotLoggedInError:
            print('Unable to log in.')
        except KeyboardInterrupt:
            print('Shutting down.')
            break
        except pycurl.error as e:
            print('pycurl error:', e)
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
