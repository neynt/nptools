#!/usr/bin/env python3
import time
import sys
import random

import lib

def kacheek_seek():
    while True:
        game = random.randint(0, 31)
        print(f"Playing hide-n-seek on map {game}.", end='', flush=True)
        path = f'/games/hidenseek/{game}.phtml?xfn='
        np = lib.NeoPage(path)
        links = np.findall(r'/games/process_hideandseek.phtml\?p=\d+&game=\d+')
        random.shuffle(links)
        for link in links:
            np.get(path)
            time.sleep(0.1)
            np.get(link)
            if np.contains('you found me'):
                amount = np.search(r'You win <b>(.*?)</b> Neopoints')[1]
                print(f' Won {amount} NP!')
                break
            elif np.contains('SO BORED'):
                print(' Your pet is bored.')
                return
            else:
                print('.', end='', flush=True)
            time.sleep(random.uniform(1.0, 1.5))
        else:
            print('?')

if __name__ == '__main__':
    kacheek_seek()
