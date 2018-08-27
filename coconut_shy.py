#!/usr/bin/env python3

import random
from urllib.parse import parse_qs

import lib

def coconut_shy():
    np = lib.NeoPage('/halloween/coconutshy.phtml')
    if np.contains('Come back tomorrow'):
        print('Coconut Shy: Already done today.')

    swf_url = np.search(r"new SWFObject\('(.*?)',")[1]
    swf = lib.NeoPage()
    while True:
        swf.set_referer(swf_url)
        swf.post(f'/halloween/process_cocoshy.phtml?coconut=1&r={random.randint(1, 99999)}')

        result = parse_qs(swf.content)
        points = int(result['points'][0])
        totalnp = int(result['totalnp'][0])
        success = int(result['success'][0])
        error = result['error'][0]

        if success == 0:
            print('Coconut Shy: Done enough.')
            break
        else:
            print(f'Coconut Shy: Made {points - 100} NP. Success code {success}. Now have {totalnp} NP. {error}')

if __name__ == '__main__':
    coconut_shy()
