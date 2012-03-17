#!/usr/bin/python2

from neo import *

c.setopt(c.URL, "http://www.neopets.com/")
c.setopt(c.POST, 1)
c.setopt(c.POSTFIELDS, "")
seed()
p1 = content.find("You have received")
if(p1 > 0):
    p2 = content.find("<br>", p1)
    print(content[p1:p2])
else:
    print("Couldn't find it.")