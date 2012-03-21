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
c.setopt(c.USERAGENT, "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)")

def dump_content():
    open("dump.html", "w").write(storage.getvalue())
    return

def seed():
    global content
    storage.truncate(0)
    c.perform()
    __builtin__.content = storage.getvalue()
    dump_content()
