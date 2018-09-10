import random
import re

import lib

path = '/medieval/grumpyking.phtml'
path2 = '/medieval/grumpyking2.phtml'
fixed_parts = dict(zip(
    (f'qp{n}' for n in range(1, 11)),
    'What,do,you do if,,fierce,Peophins,,has eaten too much,,tin of olives'.split(',')
))

def make_params(parts, fixed_parts={}):
    params = []
    for qa, n, options in parts:
        options = re.findall(r'<option value="(.*?)"', options)
        options.remove('none')
        name = f'{qa}p{n}'
        choice = fixed_parts.get(name)
        if choice == None:
            choice = random.choice(options)
        params.append(f'{name}={choice}')
    return params

def grumpy_king():
    np = lib.NeoPage()
    for _ in range(2):
        np.get(path)
        parts = np.findall(r'<div id="(.)p(\d+)Div">(.*?)</div>')
        params = make_params(parts, fixed_parts)
        print(f'Grumpy King: Asking {params}')
        np.post(path2, *params)
        result = np.search(r'''<div align='center'>(.*?)<br clear="all">''')[1]
        result = lib.strip_tags(result)
        print(f'Grumpy King: {result}')
        if 'already told me a joke today' in result:
            break

if __name__ == '__main__':
    grumpy_king()
