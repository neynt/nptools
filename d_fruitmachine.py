#!/usr/bin/python2

from neo import *

c.setopt(c.URL, "http://www.neopets.com/desert/fruitmachine.phtml")
storage.truncate(0); c.perform(); content = storage.getvalue()
p1 = content.find("Spin the Wheel!!!")
if(p1 > 0):
    c.setopt(c.URL, "http://www.neopets.com/desert/fruitmachine2.phtml")
    c.setopt(c.POST, 1)
    storage.truncate(0); c.perform(); content = storage.getvalue()
    
    p1 = content.find("The Neopets Fruit Machine</b><p>")
    if(p1 > 0):
        p1 = content.find("<img src", p1)
        p1 = content.find("<div align='center'>", p1)
        p2 = content.find("</div>", p1)
        x = content.find("You have already played")
        if(p2 > 0):
            print("Fruit machine: " + content[p1+20:p2])
        elif(x > 0):
            print("Already played fruit machine today.")
        else:
            print("Diff fruit reward??")
            
    else:
        print("Fruit machine broke.")
else:
    print("Couldn't do fruit machine.")