#!/usr/bin/env python3
import lib

def forgotten_shore():
    np = lib.NeoPage('/pirates/forgottenshore.phtml')
    if np.contains('already searched the coast'):
        print('Forgotten shore: Already searched today.')
    elif np.contains('nothing of interest to be found'):
        print('Forgotten shore: Nothing today.')
    elif np.contains('A deserted shore stretches'):
        print("Forgotten shore: Has something! http://www.neopets.com/pirates/forgottenshore.phtml")
    else:
        print('Forgotten shore not yet unlocked?')

if __name__ == '__main__':
    forgotten_shore()
