#!/usr/bin/python2

from neo import *
import itemdb

for i in range(0, 600, 30):
    c.setopt(c.URL, "http://www.neopets.com/safetydeposit.phtml?offset=" + str(i) + "&obj_name=&category=0")
    seed()
    content = storage.getvalue()
    b = 0
    for j in range(0, 30):
        if(j == 0):
            b = content.find("<tr bgcolor='#F6F6F6'>", b)
        else:
            b = content.find("Remove One", b+1)
        w = content.find("<b>", b)+3
        wd = content.find("<br>", w)
        name = content[w:wd]
        print(name)
        worth = itemdb.get_item_worth(name)
        print("   is worth " + str(worth) + " NP")
    time.sleep(3)
