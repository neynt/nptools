#!/usr/bin/env python3

import lib

path = '/desert/fruit/index.phtml'

def fruit_machine():
    np = lib.NeoPage(path)
    if np.contains('Spin, spin, spin!'):
        ck = np.search(r'<input type="hidden" name="ck" value="(.*?)">')[1]
        np.post(path, 'spin=1', f'ck={ck}')
        prize = np.search(r'<div id="fruitResult">(.*?)</div>')[1].strip()
        print(f'Fruit machine: {prize}')
    elif np.contains('already had your free spin'):
        print('Fruit machine: Already played.')
    else:
        print('Fruit machine: Error!')

if __name__ == '__main__':
    fruit_machine()
