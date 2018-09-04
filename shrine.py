#!/usr/bin/env python3

import re

import lib

def shrine():
    np = lib.NeoPage('/desert/shrine.phtml')
    np.post('/desert/shrine.phtml', 'type=approach')
    if np.contains('shrine_win.gif'):
        result = np.findall(r'<p>.*?<br clear="all">')[0]
        result = re.search(r'<div align="center">(.*?)</form>', result)[1]
        results = [r.strip() for r in re.split(r'<.*?>', result) if r.strip()]
        result = ' '.join(results)
        print(f"Coltzan's Shrine: {result}")
    elif np.contains('Maybe you should wait a while'):
        print("Coltzan's Shrine: Already visited.")
    else:
        print("Coltzan's Shrine: Error.")

if __name__ == '__main__':
    shrine()
