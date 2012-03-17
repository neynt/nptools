#!/usr/bin/python2

from neo import *
from cgi import parse_qs

url = "http://www.neopets.com/halloween/process_cocoshy.phtml?coconut=1&r=" + str(random.randint(1, 99999))
c.setopt(c.URL, url)
c.perform()
content = storage.getvalue()
"""
qs = parse_qs(content)
print("NP: %s | PROFIT: %s | MESSAGE: %s" % (qs['totalnp'][0], str(int(qs['points'][0])-100), qs['error'][0]))
"""
print(content)
