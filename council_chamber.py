#!/usr/bin/env python3

import lib

path = '/altador/council.phtml'

def council_chamber():
    np = lib.NeoPage(path)
    prhv = np.search(r'\?prhv=(.*?)">')[1]
    if not prhv:
        print('Problem with getting prhv.')
        return
    np.get(path, f'prhv={prhv}')
    if np.contains('already received your free prize today'):
        print('Already got prize from King Altador today.')
        return
    np.post(path, f'prhv={prhv}', 'collect=1')
    if np.contains('King Altador hands you your gift'):
        prize = np.search(r'King Altador hands you your gift.*?<B>(.*?)</B>')[1]
        print(f'Got {prize} from King Altador.')
    else:
        print('Problem getting gift from King Altador.')

if __name__ == '__main__':
    council_chamber()
