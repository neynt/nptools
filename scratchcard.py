#!/usr/bin/env python3

import lib

def buy_scratchcard():
    lib.inv.ensure_np(1200)
    np = lib.NeoPage('/halloween/scratch.phtml')
    np.post('/halloween/process_scratch.phtml')
    if np.contains('Hey, give everybody else a chance'):
        print('Scratchcard: Already bought.')
    else:
        print('Bought a scratchcard???')
