#!/usr/bin/python2

from neo import *

c.setopt(c.URL, "http://www.neopets.com/worlds/geraptiku/process_tomb.phtml")
c.setopt(c.REFERER, "http://www.neopets.com/worlds/geraptiku/tomb.phtml")
seed()
p1 = content.find("right on top of a Petpet.")
p2 = content.find("FIDDLESTICKS!")
x = content.find("Try again tomorrow...")
p3 = content.find("Deserted Tomb")
if(p1 > 0):
    p1 = content.find("/items/", p1)
    p2 = content.find("\" width=", p1)
    print("Deserted tomb: got item with image " + content[p1+7:p2])
elif(p2 > 0):
    print("Deserted tomb: found empty treasure chamber.")
elif(x > 0):
    print("Already did deserted tomb.")
elif(p3 > 0):
    print("Deserted tomb: different prize?")
else:
    print("Couldn't find deserted tomb.")
