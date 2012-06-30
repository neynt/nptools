#!/usr/bin/python2

from neo import *

c.setopt(c.URL, "http://www.neopets.com/pirates/forgottenshore.phtml")
seed()
d = content.find("<b>Forgotten Shore</b>")
if(d > 0):
    p1 = content.find("nothing of interest to be found today")
else:
    print("Forgotten shore has something! http://www.neopets.com/pirates/forgottenshore.phtml")