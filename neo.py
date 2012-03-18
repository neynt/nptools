#!/usr/bin/python2

from StringIO import StringIO
import pycurl
import time
import random
import sys
import __builtin__
__builtin__.content = "NONE"

random.seed()

storage = StringIO()
c = pycurl.Curl()
c.setopt(c.WRITEFUNCTION, storage.write)
c.setopt(c.COOKIEFILE, "kirls")
c.setopt(c.COOKIEJAR, "kirls")
c.setopt(c.USERAGENT, "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11")

def dump_content():
    open("dump.html", "w").write(storage.getvalue())
    return

def seed():
    global content
    storage.truncate(0)
    c.perform()
    __builtin__.content = storage.getvalue()
    dump_content()
