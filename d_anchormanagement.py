#!/usr/bin/python2

from neo import *

c.setopt(c.URL, "http://www.neopets.com/pirates/anchormanagement.phtml")
seed()
p1 = content.find("id=\"form-fire-cannon\"")
if(p1 >= 0):
    p1 = content.find("value=", p1)
    p2 = content.find("</form>", p1)
    hash = content[p1+7:p2-2]
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, "action="+hash)
    storage.truncate(0); c.perform(); content = storage.getvalue()
    
    p1 = content.find("prize-item-name\"")
    if(p1 > 0):
        p2 = content.find("</span>", p1)
        print("Blasted krawken, got " + content[p1+17:p2])
    else:
        print("Blasted krawken, indeterminate prize")
        
else:
    print("Couldn't find anchor management.")