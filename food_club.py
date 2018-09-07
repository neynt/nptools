#!/usr/bin/env python3

import lib

path = '/pirates/foodclub.phtml'

def food_club():
    np = lib.NeoPage(path)
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

if __name__ == '__main__':
    food_club()
