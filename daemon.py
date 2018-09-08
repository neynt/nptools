#!/usr/bin/env python3

from datetime import datetime, timedelta
import atexit
import os
import pickle
import time
import logging
import sys
import random

from anchor_management import anchor_management
from apple_bobbing import apple_bobbing
from bank_interest import bank_interest
from cheeseroller import cheeseroller
from coconut_shy import coconut_shy
from council_chamber import council_chamber
from deserted_tomb import deserted_tomb
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
from tombola import tombola
from trudys_surprise import trudys_surprise
from tyranu_evavu import tyranu_evavu

import lib

# Current Neopian standard time.
def now_nst():
    t = datetime.utcnow()
    t -= timedelta(hours=7)
    return t

# Does something at 6am NST next day.
def daily(last_time: datetime):
    next_time = last_time + timedelta(days=1)
    return next_time.replace(hour=4, minute=0, second=random.randint(0, 59))

def after(**kwargs):
    def f(last_time: datetime):
        return last_time + timedelta(**kwargs)
    return f

# List[Tuple[String, Callable[[], None], Callable[[datetime], datetime]]]
tasks = [
    ('trudys_surprise', trudys_surprise, daily),
    ('anchor_management', anchor_management, daily),
    ('apple_bobbing', apple_bobbing, daily),
    ('bank_interest', bank_interest, daily),
    ('council_chamber', council_chamber, daily),
    ('forgotten_shore', forgotten_shore, daily),
    ('deserted_tomb', deserted_tomb, daily),
    ('fishing', fishing, after(hours=2)),
    ('fruit_machine', fruit_machine, daily),
    ('lunar_temple', lunar_temple, daily),
    ('omelette', omelette, daily),
    ('plushie', plushie, daily),
    ('rich_slorg', rich_slorg, daily),
    ('tombola', tombola, daily),
    ('jelly', jelly, daily),
    ('shrine', shrine, daily),
    ('kacheek_seek', kacheek_seek, daily),
    ('pyramids', lambda:pyramids(True), daily),
    ('pirate_academy', pirate_academy, after(hours=1.01)),
    ('healing_springs', healing_springs, after(minutes=35)),
    ('clean inventory', lambda:lib.inv.deposit_all(exclude=['Two Dubloon Coin', 'Pant Devil Attractor']), after(hours=5)),
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
    while True:
        try:
            while True:
                now = now_nst()
                name, f, next_time = min(tasks, key=find_next_task)
                nxt = next_time(last_done[name])
                time_til = (nxt - now).total_seconds()
                if time_til > 0:
                    print(f'[Time until next action ({name}): {pprint_seconds(time_til)}]')
                    while True:
                        now = now_nst()
                        time_til = (nxt - now).total_seconds()
                        if time_til <= 0: break
                        time.sleep(min(60, time_til))
                ensure_login()
                print(f'[Doing {name}]')
                f()
                last_done[name] = now_nst()
        except lib.NotLoggedInError:
            print('Unable to log in.')
        except KeyboardInterrupt:
            print('Shutting down.')
            break
        except:
            logging.exception('')

if __name__ == '__main__':
    main()
