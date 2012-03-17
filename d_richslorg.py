#!/usr/bin/python2

from neo import *

c.setopt(c.URL, "http://www.neopets.com/shop_of_offers.phtml?slorg_payout=yes")
storage.truncate(0); c.perform(); content = storage.getvalue()
p1 = content.find("You have received <strong>");
if(p1 >= 0):
    p2 = content.find("<br>", p1)
    print(content[p1:p2])
else:
    print("Couldn't find rich slorg.")