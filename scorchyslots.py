#!/usr/bin/python2

from neo import *

hash = "";
c.setopt(c.URL, "http://www.neopets.com/games/slots.phtml")
seed()
p1 = content.find("_ref_ck")
if(p1 > 0):
    p2 = content.find("'>", p1)
    hash = content[p1+16:p2]
    print("Hash: " + hash)
else:
    print("Could not find hash")
    print(content)
lost = False;

postfields = ""

while(True):
    c.setopt(c.URL, "http://www.neopets.com/games/process_slots2.phtml")
    c.setopt(c.REFERER, "http://www.neopets.com/games/slots.phtml")
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, postfields + "_ref_ck=" + hash)
    seed()
    
    c.setopt(c.URL, "http://www.neopets.com/games/slots.phtml?hold1=&hold2=&hold3=&hold4=&play=yes")
    c.setopt(c.REFERER, "http://www.neopets.com/games/process_slots2.phtml")
    seed()
    
    np = "N/A"
    n = content.find("npanchor")
    if(n > 0):
        n = content.find(">", n)
        m = content.find("<", n)
        np = content[n+1:m]
    
    print(np + " NP")
    
    postfields = ""
    
    w = content.find("Collect Winnings")
    a = content.find("Play Again")
    xxx = content.find("BORED")
    if(w > 0):
        print("Won!")
        postfields = "collect=true&"
    elif(a > 0):
        print("Playing again.")
    elif(xxx > 0):
        print("TOTALLY BORED.")
        sys.exit()
    else:
        print("Error?")
    
    time.sleep(0.3+(random.random()/5))
