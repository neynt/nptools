#!/usr/bin/python2

import time
import urllib
import sqlite3
from neo import *

conn = sqlite3.connect('itemdb')
s = conn.cursor()

def research(name, comprensile=5):
    url = "http://www.neopets.com/market.phtml"
    data = "type=process_wizard&feedset=0&shopwizard=" + urllib.quote_plus(name) + "&table=shop&criteria=exact&min_price=0&max_price=99999"

    c.setopt(c.URL, url)
    c.setopt(c.REFERER, url)
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, data)

    times = 0
    shopper_id = {
    'a':0,'n':0,'0':0,
    'b':1,'o':1,'1':1,
    'c':2,'p':2,'2':2,
    'd':3,'q':3,'3':3,
    'e':4,'r':4,'4':4,
    'f':5,'s':5,'5':5,
    'g':6,'t':6,'6':6,
    'h':7,'u':7,'7':7,
    'i':8,'v':8,'8':8,
    'j':9,'w':9,'9':9,
    'k':10,'x':10,'_':10,
    'l':11,'y':11,
    'm':12,'z':12
    }

    secret_shoppers = list('xxxxxxxxxxxxx')
    best_shopper = 'Could not find item.'
    best_price = 999999

    while(secret_shoppers.count('x') > 0 and times < comprensile and best_price > 1):
        seed()
        x = content.find("browseshop.phtml")
        shit = content.find("too many searches!")
        cock = content.find("I did not find anything.")
        if(x > 0):
            o = content.find("<b>", x)+3
            ob = content.find("</b>", o)
            owner = content[o:ob]
            secret_shoppers[shopper_id[owner[0].lower()]] = '.'
            n = content.find("NP", x)
            ns = content.rfind("<b>", 0, n)+3
            nb = content.find("</b>", n)-3
            nps = content[ns:nb]
            np = int(nps.replace(",", ""))
            if(np <= best_price):
                print("New best price: " + nps + " at shop of " + owner + " (www.neopets.com/browseshop.phtml?owner=" + owner + ")")
                best_price = np
                best_shopper = owner
        elif(cock > 0):
            print("Found nothing.")
        elif(shit > 0):
            print("Shop wizard banned!")
            sys.exit()
        else:
            print("Could not access shop wizard!")
        times += 1
        time.sleep(0.7 + random.random())
    
    return best_price

def query_item_worth(name):
    s.execute("select worth from items where name=?", (name,))
    d = s.fetchone()
    if(d == None):
        return -1
    else:
        return d[0]

def update_item_worth(name):
    cur = query_item_worth(name)
    if(cur == -1):
        print("New item.")
        worth = research(name)
        s.execute("insert into items values (?, ?)", (name, worth))
        conn.commit()
    else:
        print("Updating. Old worth is " + str(cur))
        worth = research(name)
        s.execute("update items set worth=? where name=?", (worth, name))
        conn.commit()
    return worth

def get_item_worth(name):
    cur = query_item_worth(name)
    if(cur == -1):
        print("Not in DB. Researching...")
        worth = update_item_worth(name)
        return worth
    else:
        return cur

def add_item_worth(name, value):
    s.execute("insert into items values (?, ?)", (name, worth))
