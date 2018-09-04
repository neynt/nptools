#!/usr/bin/env python3

import lib

def tombola():
    np = lib.NeoPage('/island/tombola.phtml')
    np.post('/island/tombola2.phtml')

    if np.contains('you are only allowed one'):
        print('Tombola: Already played.')
        return

    if np.contains('YOU ARE A WINNER!!!'):
        result = np.search(r'\n<center>(.*?)\n')[1]
        print('Tombola: Won. {result}')
    elif np.contains('you win a Booby Prize'):
        prize = np.search(r'<b>Your Prize - (.*?)</b>')[1]
        print(f'Tombola: Won booby prize: {prize}')
    elif np.contains("and you don't even get a booby prize"):
        print('Tombola: Lost')
    else:
        print('Tombola: Unknown result. TODO')

if __name__ == '__main__':
    tombola()
