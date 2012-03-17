#!/usr/bin/python2

from neo import *

c.setopt(c.URL, "http://www.neopets.com/pirates/forgottenshore.phtml")
storage.truncate(0); c.perform(); content = storage.getvalue()
p1 = content.find("nothing of interest to be found today")
if(p1 >= 0):
    print("Nothing at forgotten shore.")
else:
    print("Forgotten shore has something! http://www.neopets.com/pirates/forgottenshore.phtml")