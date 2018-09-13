#!/usr/bin/env python3
import pycurl
import atexit
import datetime
import logging
import os
import pickle
import sys
import time

from anchor_management import anchor_management
from apple_bobbing import apple_bobbing
from bank_interest import bank_interest
from cheeseroller import cheeseroller
from coconut_shy import coconut_shy
from council_chamber import council_chamber
from deserted_tomb import deserted_tomb
from faerie_caverns import faerie_caverns
from fishing import fishing
from forgotten_shore import forgotten_shore
from fruit_machine import fruit_machine
from healing_springs import healing_springs
from jelly import jelly
from kacheek_seek import kacheek_seek
from lunar_temple import lunar_temple
from omelette import omelette
from pirate_academy import pirate_academy
from plushie import plushie
from pyramids import pyramids
from rich_slorg import rich_slorg
from shrine import shrine
from snowager import snowager
from stock_market import stock_market
from tombola import tombola
from trudys_surprise import trudys_surprise
from tyranu_evavu import tyranu_evavu
from grumpy_king import grumpy_king
from wise_king import wise_king
from plushie_tycoon import plushie_tycoon
from battledome import battledome

import lib
import neotime
from neotime import daily, now_nst

# List[Tuple[String, Callable[[], None], Callable[[datetime], Optional[datetime]]]]
tasks = [
    ('anchor_management', anchor_management, daily(0)),
    ('apple_bobbing', apple_bobbing, daily(0)),
    ('bank_interest', bank_interest, daily(0)),
    ('clean inventory', lambda:lib.inv.deposit_all_items(exclude=['Two Dubloon Coin', 'Pant Devil Attractor']), neotime.after(hours=5)),
    ('council_chamber', council_chamber, daily(0)),
    ('deserted_tomb', deserted_tomb, daily(0)),
    ('faerie_caverns', faerie_caverns, daily(0)),
    ('fishing', fishing, neotime.after(hours=2)),
    ('forgotten_shore', forgotten_shore, daily(0)),
    ('fruit_machine', fruit_machine, daily(0)),
    ('healing_springs', healing_springs, neotime.after(minutes=35)),
    ('jelly', jelly, daily(0)),
    ('kacheek_seek', kacheek_seek, daily(30)),
    ('lunar_temple', lunar_temple, daily(0)),
    ('omelette', omelette, daily(0)),
    ('pirate_academy', pirate_academy, neotime.immediate),
    ('plushie', plushie, daily(0)),
    ('pyramids', lambda:pyramids(True), daily(30)),
    ('rich_slorg', rich_slorg, daily(0)),
    ('shrine', shrine, neotime.after(hours=12, minutes=1)),
    ('snowager', snowager, neotime.next_snowager_time),
    ('stock_market', stock_market, daily(15)),
    ('tombola', tombola, daily(0)),
    ('trudys_surprise', trudys_surprise, daily(0)),
    ('grumpy_king', grumpy_king, neotime.skip_lunch(daily(0))),
    ('wise_king', wise_king, neotime.skip_lunch(daily(0))),
    ('plushie_tycoon', plushie_tycoon, neotime.after(minutes=15)),
    ('battledome', battledome, daily(30)),
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
