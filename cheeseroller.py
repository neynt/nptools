#!/usr/bin/python2

from neo import *

url = "http://www.neopets.com/medieval/cheeseroller.phtml"
c.setopt(c.URL, url)
c.setopt(c.REFERER, url)
seed()

ingame = True;

while(True):
    c.setopt(c.POST, 1)
    if(ingame):
        c.setopt(c.POSTFIELDS, "cheese_action=" + str(4));
    else:
        c.setopt(c.POSTFIELDS, "cheese_name=Spicy+Juppie&type=buy")
        ingame = True;
    
    seed()

    f1 = content.find("DISTANCE TO FINISH LINE")
    f2 = content.find("finish_cheese_race.gif")
    f3 = content.find("Enter name of cheese")
    f32 = content.find("GO!!!!")
    f4 = content.find("Sorry, you can only play 3")
    if(f1 >= 0):
        f2 = content.find("<br>", f1)
        f3 = content.find("TIME TAKEN", f2)
        f4 = content.find("</center>", f3)
        print("DIST: %s TIME: %s" % (content[f1+30:f2], content[f3+17:f4]))
    elif(f2 >= 0):
        f1 = content.find("finish_cheese_race.gif")
        f2 = content.find("<b>", f1)
        f3 = content.find("</b>", f2)
        f4 = content.find("</b> :", f3)
        f5 = content.find("<br>", f4)
        f6 = content.find("Your Rating", f5)
        f7 = content.find("</center>", f6)
        print("%s SCORE: %s RATING: %s" % (content[f2+3:f3], content[f4+7:f5], content[f6+16:f7]))
        ingame = False
    elif(f3 >= 0 or f32 >= 0):
        print("Starting new game...")
        ingame = False
    elif(f4 >= 0):
        print("PLAYED TOO MUCH")
        sys.exit(0)
    else:
        print(content)
    time.sleep(0.7+random.random())
