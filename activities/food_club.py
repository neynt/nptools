#!/usr/bin/env python3
# TODO: Check an external website for odds changes and take those into account.

from collections import defaultdict
import glob
import os
import time
from datetime import datetime, timedelta
import re
import json

import pandas as pd

from lib import NeoPage, util, neotime

path = '/pirates/foodclub.phtml'

pirate_names = {
    1: "Dan",
    2: "Sproggie",
    3: "Orvinn",
    4: "Lucky",
    5: "Edmund",
    6: "Peg Leg",
    7: "Bonnie",
    8: "Puffo",
    9: "Stuff",
    10: "Squire",
    11: "Crossblades",
    12: "Stripey",
    13: "Ned",
    14: "Fairfax",
    15: "Gooblah",
    16: "Franchisco",
    17: "Federismo",
    18: "Blackbeard",
    19: "Buck",
    20: "Tailhook",
}
food_names = {
    1: "Hotfish",
    2: "Broccoli",
    3: "Wriggling Grub",
    4: "Joint Of Ham",
    5: "Rainbow Negg",
    6: "Streaky Bacon",
    7: "Ultimate Burger",
    8: "Bacon Muffin",
    9: "Hot Cakes",
    10: "Spicy Wings",
    11: "Apple Onion Rings",
    12: "Sushi",
    13: "Negg Stew",
    14: "Ice Chocolate Cake",
    15: "Strochal",
    16: "Mallowicious Bar",
    17: "Fungi Pizza",
    18: "Broccoli and Cheese Pizza",
    19: "Bubbling Blueberry Pizza",
    20: "Grapity Slush",
    21: "Rainborific Slush",
    22: "Tangy Tropic Slush",
    23: "Blueberry Tomato Blend",
    24: "Lemon Blitz",
    25: "Fresh Seaweed Pie",
    26: "Flaming Burnumup",
    27: "Hot Tyrannian Pepper",
    28: "Eye Candy",
    29: "Cheese and Tomato Sub",
    30: "Asparagus Pie",
    31: "Wild Chocomato",
    32: "Cinnamon Swirl",
    33: "Anchovies",
    34: "Flaming Fire Faerie Pizza",
    35: "Orange Negg",
    36: "Fish Negg",
    37: "Super Lemon Grape Slush",
    38: "Rasmelon",
    39: "Mustard Ice Cream",
    40: "Worm and Leech Pizza",
}
arena_names = ["Shipwreck", "Lagoon", "Treasure", "Hidden", "Harpoon"]

# back when we attempted to scrape round data ourselves.
# now we use neofoodclub.fr, but let's keep this here just in case.
def food_club_old():
    np = NeoPage(path)
    np.get(path, 'type=bet')
    arenas = np.findall(r"<script language='javascript'>(.*?)</script>")
    for i,arena in enumerate(arenas[:5]):
        pirates = arena.strip().splitlines()
        pirate_odds = []
        for pirate in pirates:
            tokens = pirate.split()
            pirate_id = int(tokens[0].split('[')[1][:-1])
            odds = int(tokens[2][:-1])
            pirate_odds.append((pirate_id, odds))
        print(f'Arena {i}: {pirate_odds}')
        ar = sum(1/x for _,x in pirate_odds)
        print(ar)

def dl_fc_history(start, end):
    os.makedirs('food_club', exist_ok=True)
    nfc = NeoPage(base_url='http://neofoodclub.fr')
    for cur_round in range(start, end+1):
        print(cur_round)
        nfc.get(f'/rounds/{cur_round}.json')
        nfc.save_to_file(f'food_club/{cur_round}.json')
        time.sleep(2.0)

def stats():
    wins = defaultdict(int)
    total = defaultdict(int)
    for f in glob.glob('food_club/*.json'):
        data = json.load(open(f))
        for arena in range(5):
            for p in data['pirates'][arena]:
                total[p] += 1
        for arena, w in enumerate(data['winners']):
            wins[data['pirates'][arena][w - 1]] += 1
    for p in wins:
        print(f'{pirate_names[p]}: {wins[p]} / {total[p]} ({wins[p] / total[p]})')

def no_none(l):
    return [x for x in l if x != None]

def food_club():
    np = NeoPage(path)
    np.get(path, 'type=bet')
    maxbet = util.amt(re.search(r'You can only place up to <b>(.*?)</b> NeoPoints per bet', np.content)[1])
    print(maxbet)

    day = int(re.search(r'Next match: <b>.*?</b> the <b>(\d+).*?</b> at <b>02:00 PM NST</b>', np.content)[1])
    date = neotime.now_nst().replace(day=day, hour=14, minute=0, second=0)
    epoch = datetime(2018, 10, 7, 14, 0, 0)
    from_epoch = round((date - epoch) / timedelta(days=1))
    cur_round = 7093 + from_epoch
    print(cur_round)

    nfc = NeoPage(base_url='http://neofoodclub.fr')
    nfc.get(f'/rounds/{cur_round}.json')
    data = json.loads(nfc.content)
    print(data)
    pirates = data['pirates']
    opening_odds = data['openingOdds']

    for i, arena in enumerate(arena_names):
        print(f'=== {arena} Arena ===')
        participants = ', '.join(pirate_names[p] for p in pirates[i])
        print(f'Pirates: {participants}')
        min_probs = [None if n == 2 else 0 if n == 13 else 1/(n+1) for n in opening_odds[i][1:]]
        max_probs = [None if n == 2 else 1/n for n in opening_odds[i][1:]]
        remaining_min_prob = 1 - sum(no_none(min_probs))
        remaining_max_prob = 1 - sum(no_none(max_probs))
        left = min_probs.count(None)
        min_probs = [remaining_max_prob / left if x == None else x for x in min_probs]
        max_probs = [remaining_min_prob / left if x == None else x for x in max_probs]
        exp_probs = [(lo + hi) / 2 for lo, hi in zip(min_probs, max_probs)]
        print(min_probs)
        print(max_probs)
        print(exp_probs)

if __name__ == '__main__':
    stats()
    #dl_fc_history(6676, 6999)
    #food_club()
