#!/usr/bin/python2

from neo import *

c.setopt(c.URL, "http://www.neopets.com/faerieland/caverns/index.phtml")
c.setopt(c.REFERER, "http://www.neopets.com/faerieland/caverns/index.phtml")
c.setopt(c.POST, 1)
c.setopt(c.POSTFIELDS, "play=1")
playing = True
while(playing):
    seed()
    p1 = content.find("caverns/faerie_cave")
    x = content.find("already visited today", p1)
    if(x > 0):
        print("Already did faerie caverns.")
        playing = False
    elif(p1 > 0):
        x = content.find("faerie_cave_dead_end.gif", p1)
        if(x > 0):
            print("Dead end!")
            playing = False
        else:
            print("Faerie caverning...")
    else:
        print("Couldn't find faerie caverns.")
        playing = False
