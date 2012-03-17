#!/usr/bin/python2

from neo import *

c.setopt(c.URL, "http://www.neopets.com/shenkuu/lunar/?show=puzzle")
storage.truncate(0); c.perform(); content = storage.getvalue()
p1 = content.find("<b>Lunar Temple</b>")
if(p1 > 0):
    p1 = content.find("angleKreludor=", p1)
    p2 = content.find("&", p1)
    angle = int(content[p1+14:p2])
    angle = int(((angle+191)%360)/22.5)
    print("Lunar temple phase " + str(angle))
    c.setopt(c.URL, "http://www.neopets.com/shenkuu/lunar/results.phtml")
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, "submitted=true&phase_choice="+str(angle))
    storage.truncate(0); c.perform(); content = storage.getvalue()
    p1 = content.find("Here is a fantastic reward")
    if(p1 > 0):
        p1 = content.find(".com/items/", p1)
        p2 = content.find("' border", p1)
        print("Got item with image: " + content[p1+11:p2])
    else:
        dump_content()
        print("Couldn't win lunar temple.")
else:
    print("Couldn't find lunar temple.")
    dump_content()