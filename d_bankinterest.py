#!/usr/bin/python2

from neo import *

c.setopt(c.URL, "http://www.neopets.com/bank.phtml")
storage.truncate(0); c.perform(); content = storage.getvalue()
p1 = content.find("Collect Interest (")
if(p1 >= 0):
    p2 = content.find(")", p1)
    print("Collecting " + content[p1+18:p2] + " interest...")
    c.setopt(c.URL, "http://www.neopets.com/process_bank.phtml")
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, "type=interest")
    storage.truncate(0); c.perform()
else:
    print("Couldn't find bank interest.")