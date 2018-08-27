#!/usr/bin/env python3

import lib
import re

def pyramids():
    np = lib.NeoPage('/games/pyramids/index.phtml')
    np.post('/games/pyramids/pyramids.phtml')

    cur_card = np.search(r"<a href='pyramids.phtml\?action=draw'><img .*?>.*?<img src='.*?games/mcards/(.*?).gif'")[1]

    cards = []
    rows = np.findall(r"\n<td align='center'>(.*?)</td>")
    for row in rows:
        cards.append(re.findall(r'images.neopets.com/(.*?).gif', row))

    print(cur_card)
    print(cards)

if __name__ == '__main__':
    pyramids()
