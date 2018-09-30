#!/usr/bin/env python3

import lib

path = '/faerieland/springs.phtml'

def healing_springs():
    np = lib.NeoPage(path)
    np.post(path, 'type=heal')
    result = np.search(r'''\n<center>(.*?)<br clear="all">''')[1]
    result = lib.strip_tags(result)
    print(f'Healing springs: {result}')

if __name__ == '__main__':
    healing_springs()
