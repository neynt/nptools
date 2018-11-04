import random
from urllib.parse import parse_qs

import lib

def coconut_shy():
    log = open('coconut_shy.log', 'a')
    np = lib.NeoPage('/halloween/coconutshy.phtml')
    if np.contains('Come back tomorrow'):
        print('Coconut Shy: Already done today.')
        return
    swf_url = np.search(r"new SWFObject\('(.*?)',")[1]
    swf = lib.NeoPage()
    total_profit = 0
    while True:
        swf.set_referer(swf_url)
        swf.post(f'/halloween/process_cocoshy.phtml?coconut=1&r={random.randint(1, 99999)}')

        result = parse_qs(swf.content)
        log.write(f'{result}\n')
        points = int(result['points'][0])
        totalnp = int(result['totalnp'][0])
        success = int(result['success'][0])
        error = result['error'][0]

        if success == 0:
            print('Coconut Shy: Done enough.')
            break
        else:
            profit = points - 100
            print(f'Coconut Shy: Made {profit} NP. Code {success}. {error}')
            if points > 300:
                print(result)
            total_profit += profit
    print(f'Coconut Shy: Made {total_profit} NP in total.')

if __name__ == '__main__':
    coconut_shy()
