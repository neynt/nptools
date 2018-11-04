import random
import re

import lib

path = '/medieval/wiseking.phtml'
path2 = '/medieval/process_wiseking.phtml'

from activities.grumpy_king import make_params

def wise_king():
    np = lib.NeoPage()
    for _ in range(1):
        np.get(path)
        if np.contains('try back in an hour'):
            print(f'Wise King: At lunch.')
            return
        parts = np.findall(r'<div id="(.)p(\d+)Div">(.*?)</div>')
        params = make_params(parts)
        params_hum = ' '.join(p.split('=')[1] for p in params)
        print(f'Wise King: Saying: {params_hum}')
        np.post(path2, *params)
        if np.contains('you have already regaled'):
            print(f'Wise King: Already done.')
        else:
            result = np.search(r'''<div align='center'>(.*?)<br clear="all">''')[1]
            result = lib.strip_tags(result)
            print(f'Wise King: {result}')

if __name__ == '__main__':
    wise_king()
