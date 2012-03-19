#!/usr/bin/python2

from neo import *

hash = "";
c.setopt(c.URL, "http://www.neopets.com/games/dicearoo.phtml")
storage.truncate(0); c.perform(); content = storage.getvalue()
p1 = content.find("_ref_ck")
if(p1 > 0):
    p2 = content.find("'>", p1)
    hash = content[p1+16:p2]
    print("Hash: " + hash)
else:
    print("Could not find hash")
    print(content)

c.setopt(c.URL, "http://www.neopets.com/games/play_dicearoo.phtml");
c.setopt(c.REFERER, "http://www.neopets.com/games/play_dicearoo.phtml")
c.setopt(c.POST, 1)
lost = False;

while(True):
#for i in range(1, 100):
    storage.truncate(0)
    if(lost):
        c.setopt(c.POSTFIELDS, "type=start&raah=init&_ref_ck=" + hash)
        lost = False
    else:
        c.setopt(c.POSTFIELDS, "raah=continue&_ref_ck=" + hash)
    c.perform()
    content = storage.getvalue()
    place = content.find("<td bgcolor=")
    if(place < 0):
        place = content.find("SO BORED")
        if(place < 0):
            lost = True
            print("Starting a new game...")
        else:
            print("Your pet is SO BORED of dice-a-roo.")
            sys.exit(0);
    else:
        p2 = content.find("</b>", place)
        p3 = content.find("<i>", p2)
        p4 = content.find("</i>", p3)
        
        ps1 = content.find("Stop playing and collect", p4)
        ps2 = content.find("\"></form>", ps1)
        
        if(ps1<0):
            print("[%s] %s" % (content[place+38:p2], content[p3+3:p4]))
        else:
            print("[%s][%s] %s" % (content[place+38:p2], content[ps1+25:ps2], content[p3+3:p4]))
    
    time.sleep(1.5+random.random())
