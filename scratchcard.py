#!/usr/bin/env python3

import lib

def buy_scratchcard():
    np = lib.NeoPage('/halloween/scratch.phtml')
    np.post('/halloween/process_scratch.phtml')
