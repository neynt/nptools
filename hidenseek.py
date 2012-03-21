#!/usr/bin/python2

from neo import *
import time
import sys
import random

c.setopt(c.REFERER, "http://www.neopets.com/games/hidenseek/21.phtml")

while(True):
    for i in range(1, 10):
        c.setopt(c.URL, "http://www.neopets.com/games/process_hideandseek.phtml?p=" + str(i) + "&game=21")
        seed()
        
        print("Trying position " + str(i))
        
        w = content.find("you found me")
        x = content.find("SO BORED")
        if(w > 0):
            wn = content.find("<b>", w) + 3
            wm = content.find("</b>", wn)
            print("Got " + content[wn:wm] + " NP")
        elif(x > 0):
            print("Your pet is SO BORED")
            sys.exit()
        else:
            print("Nope.")
        time.sleep(random.random() + 4.9)
