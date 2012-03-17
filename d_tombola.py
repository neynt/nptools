#!/usr/bin/python2

from neo import *

c.setopt(c.URL, "http://www.neopets.com/island/tombola2.phtml")
c.setopt(c.REFERER, "http://www.neopets.com/island/tombola.phtml")
seed()
p1 = content.find("You put your hand into the Tombola")
x = content.find("you are only allowed one")
if(p1 > 0):
    w1 = content.find("YOU ARE A WINNER!!!")
    w2 = content.find("you win a Booby Prize!!!")
    x = content.find("and you don't even get a booby prize")
    if(w1 > 0):
        w2 = content.find("You Win", w1)
        w3 = content.find("Neopoints", w2)
        print("Tombola: Won " + content[w2+8:w3-1] + " NP")
        w2 = content.find("items/", w2)
        w3 = content.find("' width=", w2)
        print("Tombola: Won item with image " + content[w2+6:w3])
        w2 = content.find("items/", w3)
        w3 = content.find("' width=", w2)
        print("Tombola: Won item with image " + content[w2+6:w3])
    elif(w2 > 0):
        w2 = content.find("<b>Your Prize - ", w2)
        w3 = content.find("</b>", w2)
        print("Tombola: Won " + content[w2+16:w3])
    elif(x > 0):
        print("Tombola: Lost. :(")
    else:
        print("May or may not have won tombola?")
elif(x > 0):
    print("Already did tombola.")
else:
    print("Couldn't find tombola.")