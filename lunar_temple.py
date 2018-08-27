#!/usr/bin/env python3

import lib

def lunar_temple():
    np = lib.NeoPage('/shenkuu/lunar/')
    np.get('/shenkuu/lunar/?show=puzzle')
    if np.contains('once per day'):
        print('Already did lunar temple.')
        return

    angle_kreludor = int(np.search(r'angleKreludor=(\d+)')[1])
    phase = int(((angle_kreludor + 191) % 360) / 22.5)
    print(f'Lunar temple: Phase {phase}.', end='')

    np.post('/shenkuu/lunar/results.phtml', 'submitted=true', f'phase_choice={phase}')
    if np.contains('That is the correct answer'):
        prize = np.search(r'Here is a fantastic reward .*?images.neopets.com/items/(.*?)\'')[1]
        print(f'Got item with image {prize}')
    else:
        print('Error. TODO')

if __name__ == '__main__':
    lunar_temple()
