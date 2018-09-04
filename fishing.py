#!/usr/bin/env python3

import lib

path = '/water/fishing.phtml'

def fishing():
    np = lib.NeoPage(path)
    np.post(path, go_fish=1)
    if np.contains('You reel in your line and get...'):
        prize = np.search('get...<P><CENTER>.*?<B>(.*?)</B>')[1]
        print(f'Underwater fishing: Got {prize}')
    else:
        print("Couldn't find underwater fishing.")

if __name__ == '__main__':
    fishing()
