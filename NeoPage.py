#!/usr/bin/python2

import time
import re
import StringIO
import pycurl

c = pycurl.Curl()
storage = StringIO.StringIO()

class NeoPage:
	def juice(self, regex, num=1):
		r = re.compile(regex, re.DOTALL)
		m = r.search(self.content)
		if m:
			return m.group(num)
		else:
			return False
	
	def has(self, match):
		if self.content.find(match) >= 0:
			return True
		else:
			return False
	
	def req(self, url, postdata='', referer=''):
		storage.truncate(0)
		c.setopt(c.URL, 'http://www.neopets.com' + url)
		if postdata:
			c.setopt(c.POST, 1)
			c.setopt(c.POSTFIELDS, postdata)
		else:
			c.setopt(c.POST, 0)
		
		if referer:
			c.setopt(c.REFERER, 'http://www.neopets.com' + referer)
		else:
			c.setopt(c.REFERER, '')
		
		c.perform()
		self.content = storage.getvalue()
		dmp = open('dumps/' + url.replace('/', '_') + '_' + str(int(time.time())), 'w')
		dmp.write(self.content)
		dmp.close()
	
	def __init__(self):
		self.content = "NONE"
		c.setopt(c.WRITEFUNCTION, storage.write)
		c.setopt(c.COOKIEFILE, 'npd_cookies')
		c.setopt(c.COOKIEJAR, 'npd_cookies')
		c.setopt(c.USERAGENT, 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)')
