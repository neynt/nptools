#!/usr/bin/python2

from neo import *
from xml.dom.minidom import parseString

url = "http://www.neopets.com/games/pirate_slots.php?method=spin&bet=50&lines=9&hash=5f9125858b45ddcd4e12c0458974f0b7fb9bb198&r=" + str(random.randint(1, 999999999999))
c.setopt(c.URL, url);

c.perform()
content = storage.getvalue()
dom = parseString(content)
np = dom.getElementsByTagName("user_np")

if(len(np) > 0):
    np = np[0].childNodes[0].toxml()
    np_won = str(int(dom.getElementsByTagName("np_won")[0].childNodes[0].toxml()) - 450)
    jackpot = dom.getElementsByTagName("jackpot")[0].childNodes[0].toxml()
    #pawkeet = dom.getElementsByTagName("pawkeet_bonus")[0].childNodes[0].toxml()
    tb_type = dom.getElementsByTagName("treasure_bonus")[0].getAttribute("type")
    print("NP: %s | WIN: %s | JACKPOT: %s " % (np, np_won, jackpot))
else:
    print(content)
