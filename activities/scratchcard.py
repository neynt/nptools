import lib
from lib import inventory

def buy_scratchcard():
    inventory.ensure_np(1200)
    np = lib.NeoPage('/halloween/scratch.phtml')
    np.post('/halloween/process_scratch.phtml')
    if np.contains('Hey, give everybody else a chance'):
        print('Scratchcard: Already bought.')
    else:
        print('Bought a scratchcard???')
