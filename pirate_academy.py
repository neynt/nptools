#!/usr/bin/env python3

import lib

path = '/pirates/academy.phtml'

# Goal: Trains your pet at the pirate academy, prioritizing skills in this
# order, and trying to keep all skills level: Str, Def, Hp, Mov, Lvl
# Trains level if necessary (some skill is over twice level)
# Obtains a dubloon if necessary

def pirate_academy():
    np = lib.NeoPage(path)
    # TODO

if __name__ == '__main__':
    pirate_academy()
