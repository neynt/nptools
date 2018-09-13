#!/usr/bin/env python3
import lib

path = '/pirates/forgottenshore.phtml'

def forgotten_shore():
    np = lib.NeoPage(path)
    if np.contains('already searched the coast'):
        print('Forgotten shore: Already searched today.')
    elif np.contains('nothing of interest to be found'):
        print('Forgotten shore: Nothing today.')
    elif np.contains('A deserted shore stretches'):
        _ref_ck = np.search(r"<a href='\?confirm=1&_ref_ck=(.*?)'>")[1]
        np.get(path, 'confirm=1', f'_ref_ck={_ref_ck}')
        result = np.search(r"<br>A deserted shore.*?<br><br>\n")[0]
        result = lib.strip_tags(result)
        print(f'Forgotten shore: {result}')
    else:
        print('Forgotten shore not yet unlocked?')

if __name__ == '__main__':
    forgotten_shore()
