#!/usr/bin/python2

from neo import *

c.setopt(c.URL, "http://www.neopets.com/water/fishing.phtml")
c.setopt(c.POST, 1)
c.setopt(c.POSTFIELDS, "go_fish=1")
seed()
p1 = content.find("You reel in your line and get...")
if(p1 > 0):
    p1 = content.find("<B>", p1)
    p2 = content.find("</B>", p1)
    print("Underwater fishing: Got " + content[p1+3:p2])
else:
    print("Couldn't find underwater fishing.")