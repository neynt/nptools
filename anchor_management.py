#!/usr/bin/env python3

import lib

path = '/pirates/anchormanagement.phtml'

def anchor_management():
    np = lib.NeoPage(path)
    if np.contains('form-fire-cannon'):
        action = np.search('<input name="action" type="hidden" value="(.*?)">')[1]
        np.post(path, action=action)
        if np.contains('prize-item-name'):
            prize = np.search('<span class="prize-item-name">(.*?)</span>')[1]
            print(f'Blasted krawken; got {prize}')
        else:
            print('Blasted krawken; got unknown prize')
    elif np.contains('safe from sea monsters for one day'):
        print('Already did anchor management.')
    else:
        print("Couldn't find anchor management.")

if __name__ == '__main__':
    anchor_management()
