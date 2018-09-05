#!/usr/bin/env python3

import lib

def deserted_tomb():
    np = lib.NeoPage('/worlds/geraptiku/tomb.phtml')
    if np.contains('enough excitement for one day'):
        print('Deserted tomb: Already done.')
        return
    np.post('/worlds/geraptiku/tomb.phtml', 'opened=1')
    np.post('/worlds/geraptiku/process_tomb.phtml')
    if np.contains('right on top of a Petpet.'):
        print('Deserted tomb: Got item. TODO')
    elif np.contains('EUREKA!'):
        prize = np.search(r'<strong>(.*?)</strong> <strong>Neopoints</strong>')[1]
        prize = int(prize.replace(',', ''))
        print(f'Deserted tomb: Found treasure! Got items and {prize} NP.')
    elif np.contains('FIDDLESTICKS!'):
        print('Deserted tomb: Found empty treasure chamber.')
    elif np.contains('A giant monster leaps out from the darkness'):
        print('Deserted tomb: Monster! TODO')
    elif np.contains('You watch as the arrows fly right at you'):
        print('Deserted tomb: Traps! TODO')
    elif np.contains('Deserted Tomb'):
        print('Deserted tomb: Different prize. TODO')
    else:
        print('Deserted tomb: Error.')

if __name__ == '__main__':
    deserted_tomb()
