#!/usr/bin/python2

from neo import *

c.setopt(c.URL, "http://www.neopets.com/altador/council.phtml")
storage.truncate(0); c.perform(); content = storage.getvalue()
p1 = content.find("?prhv=")
if(p1 >= 0):
    p2 = content.find("\">", p1)
    prhv = content[p1+6:p2]
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, "prhv="+prhv+"&collect=1")
    storage.truncate(0); c.perform(); content = storage.getvalue()
    
    p1 = content.find("King Altador hands you your gift...")
    if(p1 >= 0):
        p1 = content.find("<B>", p1)
        p2 = content.find("</B>", p1)
        giftname = content[p1+3:p2]
        print("Got %s from council chamber!" % giftname)
    else:
        print("Problem with retrieving gift.")
else:
    print("Problem with getting prhv.")