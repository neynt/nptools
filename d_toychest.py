#!/usr/bin/python2

from neo import *

c.setopt(c.URL, "http://www.neopets.com/petpetpark/daily.phtml")
c.setopt(c.POST, 1)
c.setopt(c.POSTFIELDS, "go=1")
storage.truncate(0); c.perform(); content = storage.getvalue()
dump_content()
p1 = content.find("You've received the following prize!");
x = content.find("You've already collected your prize");
if(p1 > 0):
    p1 = content.find("prize-item-name\">", p1)
    p2 = content.find("<BR><BR><B>")
    if(p1 > 0):
        p2 = content.find("</span>", p1)
        print("Toy chest: got " + content[p1+18:p2])
    elif(p2 > 0):
        p3 = content.find("</B>", p2)
        print("Toy chest: got " + content[p2+11:p3])
    else:
        print("Toy chest: Different prize?")
elif(x > 0):
    print("Already did toy chest")
else:
    print("Couldn't find toy chest.")