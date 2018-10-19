#!/usr/bin/env python3
# TODO: Check an external website for odds changes and take those into account.

from collections import defaultdict
import itertools
import glob
import os
import time
from datetime import datetime, timedelta
import re
import json
from dataclasses import dataclass
from typing import List

import pandas as pd
import numpy
import matplotlib.pyplot as plt

from lib import NeoPage, util, neotime

path = '/pirates/foodclub.phtml'

favorites = [
    None,
    [None,2,0,0,1,0,1,1,1,0,1,0,2,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0],
    [None,1,0,0,1,1,1,1,1,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,0,0,0,0],
    [None,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,0,0,0,1,0,1,0,0,1,0,0,1],
    [None,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,1,1],
    [None,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,1,1,0],
    [None,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,0,0,0,0,0,0],
    [None,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,1,1,0,0,0,1,0,0,1,1,0,0,0,0,0,1,0,0],
    [None,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1,1,1,1,1,0,0,0,1,0,0,1,1,0,0,0,0,1,1,0,0],
    [None,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
    [None,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0],
    [None,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,1],
    [None,1,0,0,1,0,1,1,1,0,1,0,1,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0],
    [None,1,0,0,1,0,1,1,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
    [None,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,1,0,0,0,1,1,0,1,1,0,1,1,0,0,0,1,0,0,0,0,0,0],
    [None,1,0,0,1,0,1,1,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
    [None,1,0,0,1,0,1,1,1,0,2,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,1,1,0,0,0,0,0,0],
    [None,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,2,1,1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,0,0,0,1,2],
    [None,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,1,0,0,0,1,1,0,1,1,0,1,1,0,0,0,1,0,0,0,0,0,0],
    [None,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0],
    [None,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,1,0,0,1,0,0,0,1,0,0,0,0,0,0]
]

allergies = [
    None,
    [None,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0],
    [None,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,1,1],
    [None,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
    [None,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
    [None,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0],
    [None,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0],
    [None,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,0,0,0,0,0,0],
    [None,1,0,0,1,0,1,1,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
    [None,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0],
    [None,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
    [None,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
    [None,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0],
    [None,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,1,1,0],
    [None,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
    [None,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
    [None,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0],
    [None,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0],
    [None,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,1,1,0],
    [None,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,1,0,0,1,0,0,0,1,0,0,0,0,0,0],
    [None,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0]
]

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

def no_none(l):
    return [x for x in l if x != None]

def product(l):
    result = 1
    for x in l:
        result *= x
    return result

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
        print(f'Grabbing round {cur_round} from neofoodclub')
        nfc.get(f'/rounds/{cur_round}.json')
        nfc.save_to_file(f'food_club/{cur_round}.json')
        time.sleep(2.0)

def stats():
    tbl = {}
    tbl['round'] = []
    tbl['pirate'] = []
    tbl['arena'] = []
    tbl['won'] = []
    tbl['opening_odds'] = []
    tbl['closing_odds'] = []
    tbl['food_adjustment'] = []
    tbl['prior'] = []

    for f in glob.glob('food_club/*.json'):
        data = json.load(open(f))
        for arena in range(5):
            arena_probs = []
            for i, p in enumerate(data['pirates'][arena]):
                o = data['openingOdds'][arena][i + 1]
                arena_probs.append(None if o == 2 else 0.05 if o == 13 else (2 * o + 1) / (2 * o * (o + 1)))
            rem = 1 - sum(no_none(arena_probs))
            left = arena_probs.count(None)
            arena_probs = [rem / left if x == None else x for x in arena_probs]

            for i, p in enumerate(data['pirates'][arena]):
                tbl['round'].append(data['round'])
                tbl['pirate'].append(p)
                tbl['arena'].append(arena)
                tbl['won'].append(data['winners'][arena] == i + 1)
                tbl['opening_odds'].append(data['openingOdds'][arena][i + 1])
                tbl['closing_odds'].append(data['currentOdds'][arena][i + 1])
                if 'foods' in data:
                    fa = sum(1 if favorites[p][f] else 0 for f in data['foods'][arena])
                    fa -= sum(1 if allergies[p][f] else 0 for f in data['foods'][arena])
                    tbl['food_adjustment'].append(fa)
                else:
                    tbl['food_adjustment'].append(None)
                tbl['prior'].append(arena_probs[i])

    return pd.DataFrame(tbl)

@dataclass
class Pirate:
    pirate: int
    opening_odds: int
    closing_odds: int
    food_adjustment: int

@dataclass
class Round:
    round_num: int
    pirates: List[List[Pirate]]
    winners: List[int]

def get_rounds(data) -> List[Round]:
    data = data.set_index(['round', 'arena'])
    data.sort_index(inplace=True, sort_remaining=True)
    rounds = data.index.levels[0]
    result = []
    for round_num in rounds:
        pirates = []
        winners = []
        for arena in range(5):
            round_pirates = []
            arena_data = data.loc[round_num, arena]
            for i, row in arena_data.iterrows():
                if row['won']:
                    winners.append(row['pirate'])
                round_pirates.append(Pirate(row['pirate'], row['opening_odds'], row['closing_odds'], row['food_adjustment']))
            pirates.append(round_pirates)
        result.append(Round(round_num, pirates, winners))
    return result

def all_bets():
    return itertools.product(*[[None, 0, 1, 2, 3] for _ in range(5)])

def winnings(rnd, bet):
    result = 1
    for i in range(5):
        if bet[i] != None:
            pirate = rnd.pirates[i][bet[i]]
            if rnd.winners[i] == pirate.pirate:
                result *= pirate.closing_odds
            else:
                return 0
    return result

# Strategies in general return a list of up to 10 (amt, spend, bets) tuples.
# exp is the amount the strategy expects with win on average.
# spend is the amount to bet as a fraction of the user's max bet.
# bets is a list of bets.
# A bet is a list of 5 pirate indices (or None if no bet in that arena).

# Produce a strategy given weights for each pirate in each arena. Normalized
# weights are interpreted as probabilities for each pirate to win, and after
# that, maximizing EV is straightforward.
def best_bets_from_probs(strengths, rnd, max_win):
    total_strengths = map(sum, strengths)
    probs = []
    for arena_strengths, total_strength in zip(strengths, total_strengths):
        probs.append([p / total_strength for p in arena_strengths])
    bets_by_exp_win = []
    for bet in all_bets():
        exp_win = 1
        spend = 1
        payoff = 1
        for arena_probs, arena_pirates, b in zip(probs, rnd.pirates, bet):
            if b != None:
                exp_win *= arena_probs[b] * arena_pirates[b].closing_odds
                payoff *= arena_pirates[b].closing_odds
        if payoff > max_win:
            reduction = max_win / payoff
            exp_win *= reduction
            spend *= reduction
        bets_by_exp_win.append((exp_win, spend, bet))
    bets_by_exp_win.sort(reverse=True, key=lambda x:x[0])
    return [b for b in bets_by_exp_win[:10] if b[0] > b[1]]

# Ten best bets given we can predict the winners.
def psychic_strategy(rnd, max_win):
    probs = []
    for i, arena_pirates in enumerate(rnd.pirates):
        probs.append([1 if p.pirate == rnd.winners[i] else 0 for p in arena_pirates])
    return best_bets_from_probs(probs, rnd, max_win)

# Maximize TER. We assume that Neopets calculates the true probability of each
# pirate winning the round, and sets initial odds by rounding down the fair
# odds (to a minimum of 2:1 whenever the true win chance is > 1/3). This allows
# for profit when pirates with true win probability > 0.5 get a 2:1 payoff, as
# well as when odds change favorably.
def maxter_strategy_base(get_odds):
    def strat(rnd, max_win):
        probs = []
        for arena in range(5):
            arena_probs = []
            for p in rnd.pirates[arena]:
                o = get_odds(p)
                arena_probs.append(None if o == 2 else 0.05 if o == 13 else (2 * o + 1) / (2 * o * (o + 1)))
            remaining_exp_prob = 1 - sum(no_none(arena_probs))
            left = arena_probs.count(None)
            arena_probs = [remaining_exp_prob / left if x == None else x for x in arena_probs]
            probs.append(arena_probs)
        return best_bets_from_probs(probs, rnd, max_win)
    return strat

# Standard MAXTER that uses opening odds as an estimate of probability.
maxter_strategy = maxter_strategy_base(lambda p: p.opening_odds)

# MAXTER, but uses closing odds as an estimate of probability instead.
maxter_closing_strategy = maxter_strategy_base(lambda p: p.closing_odds)

# Use past data on how often a pirate won with particular starting odds.
# Disregard rounding assumption, much to our detriment. This is really bad
# don't use it
def learn_prior_strategy(training_data):
    data = training_data.groupby(['pirate', 'opening_odds']).agg({'won': 'mean', 'pirate': 'count'}).rename(columns={'pirate': 'n'})
    data = data.reindex([(p, o) for p in range(1, 21) for o in range(2, 14)])
    def strat(rnd, max_win):
        strengths = []
        for arena in range(5):
            arena_strengths = []
            for p in rnd.pirates[arena]:
                val = data.loc[p.pirate, p.opening_odds]
                strength = val['won']
                n = val['n']
                if n < 10 or pd.isna(strength):
                    strength = ((1 / p.opening_odds) + (1 / (p.opening_odds + 1))) / 2
                arena_strengths.append(strength)
            strengths.append(arena_strengths)
        return best_bets_from_probs(strengths, rnd, max_win)
    return strat

def learn_maxter_fa_strategy(training_data):
    data = training_data
    data = data.set_index(['pirate', 'food_adjustment'])
    data.sort_index(inplace=True, sort_remaining=True)

    global d
    d = data

    fa_adj = {}

    pirates = data.index.levels[0].unique()
    for p in pirates:
        d = data.loc[p]
        fas = d.index.unique()
        for fa in fas:
            if pd.isna(fa): continue
            d = data.loc[p, fa]
            n = d['prior'].count()
            exp_wins = d['prior'].sum()
            actual_wins = d['won'].sum()
            if n > 100:
                fa_adj[p, fa] = actual_wins / exp_wins

    print(fa_adj)

    def strat(rnd, max_win):
        probs = []
        for arena in range(5):
            arena_probs = []
            for p in rnd.pirates[arena]:
                o = p.opening_odds
                arena_probs.append(None if o == 2 else 0.05 if o == 13 else (2 * o + 1) / (2 * o * (o + 1)))
            remaining_exp_prob = 1 - sum(no_none(arena_probs))
            left = arena_probs.count(None)
            arena_probs = [remaining_exp_prob / left if x == None else x for x in arena_probs]
            arena_probs = [x * fa_adj.get((p.pirate, p.food_adjustment), 1) for x, p in zip(arena_probs, rnd.pirates[arena])]
            probs.append(arena_probs)
        return best_bets_from_probs(probs, rnd, max_win)

    return strat

def backtest(strategy, test_rounds, max_win=999999):
    total_won = 0
    total_exp_win = 0
    total_spent = 0
    for rnd in test_rounds:
        round_won = 0
        round_exp_win = 0
        round_spent = 0
        for exp_win, spend, bet in strategy(rnd, max_win):
            won = spend * winnings(rnd, bet)
            round_won += won
            round_exp_win += exp_win
            round_spent += spend
            #print(f'Arena: {won} (expected {exp_win}, spent {spend})')
        total_won += round_won
        total_exp_win += round_exp_win
        total_spent += round_spent
        #print(f'{rnd.round_num}: {round_won} (expected {round_exp_win}, spent {round_spent})')
    print(f'                   Units won: {total_won:.2f}')
    print(f'                 Units spent: {total_spent:.2f}')
    print(f'               Effective TER: {total_won / total_spent * 10:.2f}')
    print(f"Strategy's expected winnings: {total_exp_win:.2f}")
    print(f"Real performance v. expected: {100 * (total_won / total_exp_win - 1):+.2f}%")
    return total_won, total_exp_win, total_spent

def experiment():
    table = stats()
    strategies = [
        ('psychic', lambda _: psychic_strategy),
        ('maxter', lambda _: maxter_strategy),
        #('maxter_close', lambda _: maxter_closing_strategy),
        ('maxter_fa', learn_maxter_fa_strategy),
        #('priors', learn_prior_strategy),
    ]
    # Cross-validation
    N_SPLITS = 9
    total_won = {k: 0 for k,v in strategies}
    total_exp_win = {k: 0 for k,v in strategies}
    total_spent = {k: 0 for k,v in strategies}
    for split in range(N_SPLITS):
        training_data = table[table['round'] % N_SPLITS != split]
        test_data     = table[(table['round'] % N_SPLITS == split) & (table['round'] <= 7095)]
        test_rounds   = get_rounds(test_data)
        for name, strategy in strategies:
            won, exp_win, spent = backtest(strategy(training_data), test_rounds, 1000000 / 7924)
            total_won[name] += won
            total_exp_win[name] += exp_win
            total_spent[name] += spent

    print(f'{"Strategy": >15} {"Won": >10} {"Spent": >10} {"Eff TER": >10}')
    for name, _ in strategies:
        won = total_won[name]
        spent = total_spent[name]
        eff_ter = won / spent * 10
        print(f'{name: >15} {won: >10.2f} {spent: >10.2f} {eff_ter: >10.2f}')

def food_club():
    np = NeoPage(path)
    np.get(path, 'type=bet')
    maxbet = util.amt(re.search(r'You can only place up to <b>(.*?)</b> NeoPoints per bet', np.content)[1])
    print(f'Max bet is {maxbet}')

    # We compute the current round number because it seems there's no way to
    # find it explicitly unless you actually make a bet.
    day = int(re.search(r'Next match: <b>.*?</b> the <b>(\d+).*?</b> at <b>02:00 PM NST</b>', np.content)[1])
    date = neotime.now_nst().replace(day=day, hour=14, minute=0, second=0)
    epoch = datetime(2018, 10, 7, 14, 0, 0)
    from_epoch = round((date - epoch) / timedelta(days=1))
    cur_round = 7093 + from_epoch
    print(f'Food Club round {cur_round}')

    dl_fc_history(cur_round - 1, cur_round)
    table = stats()
    rnd = get_rounds(table[table['round'] == cur_round])[0]

    for i, arena in enumerate(arena_names):
        participants = ', '.join(pirate_names[p.pirate] for p in rnd.pirates[i])
        print(f'{arena} Arena: {participants}')

    bets = maxter_strategy(rnd, 1000000 / maxbet)
    total_bet_amt = 0
    total_exp_win = 0
    TER = 0
    for exp_win, spend, bet in bets:
        if exp_win < 1.0:
            print('Not making -EV bet: {bet}')
            continue
        bet_amt = round(spend * maxbet)
        print(f'Bet {bet_amt} NP on {bet}. EV: {exp_win * bet_amt:.1f} NP')
        opts = []
        total_odds = 1
        for i, (ps, b) in enumerate(zip(rnd.pirates, bet)):
            if b == None:
                continue
            ps[b].pirate
            opts.append(f'winner{i+1}={ps[b].pirate}')
            opts.append(f'matches[]={i+1}')
            total_odds *= ps[b].closing_odds
        opts.append(f'bet_amount={bet_amt}')
        opts.append(f'total_odds={total_odds}')
        opts.append(f'winnings={bet_amt * total_odds}')
        opts.append('type=bet')
        np.post('/pirates/process_foodclub.phtml', *opts)
        total_bet_amt += bet_amt
        total_exp_win += bet_amt * exp_win
        TER += exp_win

    print(f'Made {total_bet_amt} NP of bets. Expect to win {total_exp_win:.1f} NP. (TER {TER:.2f}; ROI {total_exp_win / total_bet_amt:.3f})')

if __name__ == '__main__':
    experiment()
    #dl_fc_history(7095, 7099)
    #food_club()
