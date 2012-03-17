#!/usr/bin/python2

from neo import *

c.setopt(c.URL, "http://www.neopets.com/halloween/applebobbing.phtml?bobbing=1")
seed()
p1 = content.find("hf_call_to_action")

if(p1 >= 0):
    p2 = content.find("</div>", p1)
    print("Bobbed apples: " + content[p1+31:p2-1])
else:
    print("Couldn't find apple bobbing.")