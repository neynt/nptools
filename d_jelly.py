#!/usr/bin/python2

from neo import *

c.setopt(c.URL, "http://www.neopets.com/jelly/jelly.phtml")
c.setopt(c.POST, 1)
c.setopt(c.POSTFIELDS, "type=get_jelly")
storage.truncate(0); c.perform(); content = storage.getvalue()
p1 = content.find("You take some")
x = content.find("You cannot take more than one jelly per day!")
if(p1 > 0):
    p1 = content.find("<b>", p1)
    p2 = content.find("</b>", p1)
    print("Giant Jelly: Got " + content[p1+3:p2])
elif(x > 0):
    print("Already got jelly today.")
else:
    print("Couldn't find giant jelly.")