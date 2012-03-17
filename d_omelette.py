#!/usr/bin/python2

from neo import *

c.setopt(c.URL, "http://www.neopets.com/prehistoric/omelette.phtml")
c.setopt(c.POST, 1)
c.setopt(c.POSTFIELDS, "type=get_omelette")
storage.truncate(0); c.perform(); content = storage.getvalue()
p1 = content.find("You approach")
x = content.find("You cannot take more than one slice per day!")
if(x > 0):
    print("Already got omelette today.")
elif(p1 > 0):
    p1 = content.find("items/", p1)
    p2 = content.find("' width=", p1)
    print("Giant Omelette: Got " + content[p1+6:p2])
else:
    print("Couldn't find giant omelette.")