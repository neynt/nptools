#!/usr/bin/env python3

import time
import json

import lib

def trudys_surprise():
    np = lib.NeoPage('/allevents.phtml')
    if not np.contains("Trudy's Surprise has reset"):
        print("Trudy's Surprise: Already done.")
        return
    else:
        # TODO test
        np.get('/trudys_surprise.phtml')
        np.post('/trudydaily/ajax/claimprize.php', 'action=beginroll')
        result = json.loads(np.content)
        print(f"Trudy's Surprise: Won {result['prizes']}. Now have {result['adjustedNP']} NP.")
        time.sleep(0.7)
        np.post('/trudydaily/ajax/claimprize.php', 'action=prizeclaimed')
        np.get('/trudys_surprise.phtml')

if __name__ == '__main__':
    trudys_surprise()
