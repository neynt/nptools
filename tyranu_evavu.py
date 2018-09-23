import random
from collections import defaultdict

import lib

nums = range(2, 15)
card_to_num = dict(zip('23456789TJQKA', nums))

def guess(card_num, counts):
    lesser = sum(counts[n] for n in nums if n < card_num)
    higher = sum(counts[n] for n in nums if n > card_num)
    if lesser < higher:
        return 'tyranu'
    elif lesser > higher:
        return 'evavu'
    else:
        return 'idk'

def reward(correct):
    if correct == 52: return 12000
    if correct >= 50: return 7200
    if correct >= 40: return 4800
    if correct >= 30: return 2388
    if correct >= 21: return 1243
    if correct >= 20: return 1116
    if correct >= 17: return 734
    if correct >= 16: return 607
    if correct >= 15: return 408
    if correct >= 14: return 362
    if correct >= 13: return 316
    if correct >= 12: return 271
    if correct >= 11: return 225
    if correct >= 10: return 156
    if correct >= 8: return 93
    if correct >= 7: return 62
    if correct >= 6: return 31
    if correct >= 5: return 18
    if correct >= 4: return 14
    if correct >= 3: return 10
    if correct >= 2: return 7
    if correct >= 1: return 3
    else: return 0

def trial():
    deck = list(nums) * 4
    random.shuffle(deck)
    correct = 0
    counts = dict(zip(nums, [4]*13))
    for cur, nxt in zip(deck, deck[1:]):
        counts[cur] -= 1
        prediction = guess(cur, counts)
        if prediction == 'idk':
            prediction = random.choice(['tyranu', 'evavu'])
        if nxt > cur and prediction != 'tyranu': break
        if nxt < cur and prediction != 'evavu': break
        correct += 1
    return correct

def stats():
    results = defaultdict(int)
    for _ in range(100000):
        results[trial()] += 1
    total = sum(results.values())
    print(f'total: {total}')
    pdf = {}
    cdf = {}
    cumul = 0
    for k,v in sorted(results.items()):
        cumul += v
        pdf[k] = v / total
        cdf[k] = cumul / total
    print(f'pdf: {pdf}')
    print(f'cdf: {cdf}')
    ev = sum(reward(k) * v for k,v in pdf.items())
    print(f'ev: {ev}')

def solve():
    counts = dict(zip(nums, [4]*13))
    while True:
        card = input().strip()[0]
        card_num = card_to_num[card]
        counts[card_num] -= 1
        g = guess(card_num, counts)
        #print(f'{g}; {lesser} lesser, {higher} higher.')
        print(g)

path = '/games/tyranuevavu.phtml'

def tyranu_evavu():
    np = lib.NeoPage(path)

    while True:
        # Start a new game.
        ref_ck = np.search(r"<input type=hidden name='_ref_ck' value='(.*?)'>")[1]
        dealer = np.search(r"<input type=hidden name='dealer' value='(\d+)'>")[1]
        np.post(path, f'_ref_ck={ref_ck}', 'type=play', 'action=shuffle', r'dealer={dealer}')

        if np.contains('played enough for today'):
            print('Tyranu Evavu: Played enough for today.')
            return

        print('Tyranu Evavu: Starting game. (-30 NP)')

        counts = dict(zip(nums, [4]*13))
        while True:
            card = np.findall(r'images.neopets.com/games/cards/(.*?)\.gif')[0]
            rank = int(card.split('_')[0])
            counts[rank] -= 1
            g = guess(rank, counts)

            if g == 'tyranu':
                print(f'{card} tyranu')
                np.post(path, 'type=play', 'action=higher')
            elif g == 'evavu':
                print(f'{card} evavu')
                np.post(path, 'type=play', 'action=lower')
            else:
                print(f'{card} idk')
                np.post(path, 'type=play', 'action=' + random.choice(['higher', 'lower']))

            if np.contains('Ugga!'):
                print(f'Good!')
                continue
            elif np.contains('Uhhg Uuuuu'):
                num_correct = np.search(r'You managed <b>(\d+)</b> correct guesses...')[1]
                prize = np.search(r"That's worth <b>(\d+) np</b>!")[1]
                print(f'Tyranu Evavu: Lost after {num_correct} rounds. Won {prize} NP.')
                ref_ck = np.search(r"<input type=hidden name='_ref_ck' value='(.*?)'>")[1]
                np.post(path, f'_ref_ck={ref_ck}', 'type=intro')
                break

if __name__ == '__main__':
    #stats()
    #solve()
    tyranu_evavu()
