#!/usr/bin/python2

from neo import *

c.setopt(c.URL, "http://www.neopets.com/faerieland/tdmbgpop.phtml")
c.setopt(c.POST, 1)
c.setopt(c.POSTFIELDS, "talkto=1")
storage.truncate(0); c.perform(); content = storage.getvalue()
open("dump.html", "w").write(content)
p1 = content.find("<div align='center'>")
x = content.find("You have already visited the plushie today")
if(p1 > 0):
    p2 = content.find("</div>", p1)
    print("Plushie: " + content[p1+20:p2])
elif(x > 0):
    print("Already visited plushie.")
else:
    print("Couldn't find plushie.")