#!/usr/bin/env python3

import lib

path = '/faerieland/tdmbgpop.phtml'

def plushie():
    np = lib.NeoPage(path)
    np.post(path, 'talkto=1')
    if np.contains("<div align='center'>"):
        result = np.search(r"<div align='center'>(.*?)</div>")[1]
        print(f'Plushie: {result}')
    elif np.contains('already visited the plushie today'):
        print('Plushie: Already visited.')
    else:
        print('Plushie: Error.')

if __name__ == '__main__':
    plushie()
