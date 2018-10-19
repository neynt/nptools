# TODO: This greedy AI is pretty good as is, but could be improved by tracking
# cards and guessing the chance that uncovered cards will extend the streak.

import random
import re
import time

import lib
from lib import neotime

# Returns all (cr, path) pairs.
# cr: The number of cards that the path reveals.
# path: A sequence of visible cards that you can play.
def all_paths(cur_card, cards):
    cur_value = int(cur_card.split('_')[0])
    playable_cards = []
    result = []
    for i, row in enumerate(cards):
        for j, card in enumerate(row):
            if card in ['?', '']: continue
            value = int(card.split('_')[0])
            if (value - cur_value) % 13 in [1, 12]:
                cards_revealed = 0
                if j > 0 and cards[i][j-1] == '': cards_revealed += 1
                if j < len(cards[i]) - 1 and cards[i][j+1] == '': cards_revealed += 1
                cards[i][j] = ''
                result.append((cards_revealed, [card]))
                for (cr, subpath) in all_paths(card, cards):
                    result.append((cards_revealed + cr, [card] + subpath))
                cards[i][j] = card
    return result

def best_move(cur_card, cards):
    paths = all_paths(cur_card, cards)
    if not paths: return None
    best_path = max(paths, key=lambda x:(x[0], len(x[1])))
    return best_path[1][0]

def pyramids():
    np = lib.NeoPage('/games/pyramids/index.phtml')
    np.post('/games/pyramids/pyramids.phtml')
    print('Pyramids: ', end='')

    while True:
        if np.contains('There are no more available moves!'):
            link = np.search(r"<b>There are no more available moves!<br><a href='(.*?)'><b>Collect Points</b>")[1]
            np.get('/games/pyramids/' + link)
            verb = 'Won'
            noun = 'NP'
            reached_limit = False
            if np.contains('You have reached the <b>5000</b> Neopoint daily limit'):
                verb = 'Got'
                noun = 'pts'
                reached_limit = True
            status = np.search(r'Congratulations.*?<b>(\d+?)</b> (Neo)?points!.*total score has been updated to <b>(.*?)</b>.*?have played <b>(.*?)</b> game.*?cleared the pyramid <b>(.*?)</b>.*?current win streak is <b>(.*?)</b>')
            print(f'\nPyramids: {verb} {status[1]} {noun}. Total: {status[3]}. Games: {status[4]}. Won: {status[5]}. Streak: {status[6]}.')
            if reached_limit:
                return neotime.daily(3)(neotime.now_nst())
            return None

        cur_card = np.search(r"&nbsp; <img src='.*?games/mcards/(.*?).gif'")[1]

        cards = []
        links = {}
        rows = np.findall(r"\n<td align='center'>(.*?)</td>")
        for row in rows:
            row_cards_raw = re.findall(r'images.neopets.com/(.*?).gif', row)
            row_cards = []
            for c in row_cards_raw:
                if 'backs' in c: row_cards.append('?')
                elif 'blank' in c: row_cards.append('')
                else: row_cards.append(c.split('/')[-1])
            row_playable_cards = [c for c in row_cards if c not in ['?', '']]
            row_links = re.findall(r"<a href='(.*?)'>", row)
            cards.append(row_cards)
            links.update(dict(zip(row_playable_cards, row_links)))

        best_card = best_move(cur_card, cards)
        cards_left = sum(1 if c else 0 for c in sum(cards, []))

        if cards_left < 10:
            print(cards_left, end='', flush=True)
        else:
            print('!' if best_card else '.', end='', flush=True)

        if best_card:
            np.get('/games/pyramids/' + links[best_card])
        else:
            np.get('/games/pyramids/pyramids.phtml?action=draw')
        time.sleep(min(random.expovariate(1/0.4), 2.0))

if __name__ == '__main__':
    while True:
        pyramids()
