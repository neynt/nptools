from collections import defaultdict
from datetime import datetime
import io
import os
import pycurl
import re
import sqlite3
import time

def strip_tags(text):
    return ' '.join([t.strip() for t in re.split(r'<.*?>', text) if t.strip()])

def amt(x):
    return int(strip_tags(x).split()[0].replace(',', ''))

def dict_to_eq_pairs(kwargs):
    return [f'{k}={v}' for k, v in kwargs.items()]

def table_to_tuples(tbl, raw=False):
    result = []
    trs = re.findall(r'<tr.*?>(.*?)</tr>', tbl, flags=re.DOTALL)
    for i,tr in enumerate(trs):
        tds = re.findall(r'<td.*?>(.*?)</td>', tr, flags=re.DOTALL)
        tds = tuple(tds) if raw else tuple(map(strip_tags, tds))
        result.append(tds)
    return result

class NotLoggedInError(Exception):
    pass

FIREFOX_COOKIES_DB = os.environ.get('FIREFOX_COOKIES_DB')
cookies_db = None
if FIREFOX_COOKIES_DB:
    cookies_db = sqlite3.connect(FIREFOX_COOKIES_DB)
USER_AGENT = os.environ.get('USER_AGENT', 'Mozilla/5.0')
COOKIE_FILE = 'nptools.cookies'

class NeoPage:
    def __init__(self, path=None):
        self.content = ''
        self.last_file_path = ''
        self.referer = ''
        self.base_url = 'http://www.neopets.com'
        if path:
            self.get(path)

    def save_to_file(self, filename):
        open(filename, 'w').write(self.content)

    def load_file(self, filename):
        self.content = open(filename, 'r').read()

    def perform(self, url, opts=[]):
        storage = io.BytesIO()
        cookie_string = None
        if cookies_db:
            c = cookies_db.cursor()
            c.execute('''
            SELECT name, value FROM moz_cookies
            WHERE baseDomain = 'neopets.com'
            ''')
            results = list(c.fetchall())
            cookie_string = ';'.join(f'{name}={value}' for name, value in results)

        curl = pycurl.Curl()
        curl.setopt(pycurl.TIMEOUT_MS, 5000)
        curl.setopt(pycurl.REFERER, self.referer)
        curl.setopt(pycurl.WRITEFUNCTION, storage.write)
        if cookie_string:
            curl.setopt(pycurl.COOKIE, cookie_string)
        else:
            curl.setopt(pycurl.COOKIEFILE, COOKIE_FILE)
        curl.setopt(pycurl.COOKIEJAR, COOKIE_FILE)
        curl.setopt(pycurl.USERAGENT, USER_AGENT)
        curl.setopt(pycurl.URL, url)
        for k, v in opts:
            curl.setopt(k, v)
        curl.perform()
        # Forces cookies to be flushed to COOKIE_FILE, I hope.
        del curl

        self.referer = url
        self.content = storage.getvalue().decode('utf-8')

        if cookies_db:
            c = cookies_db.cursor()
            for line in open(COOKIE_FILE).readlines():
                if line.startswith('#'): continue
                tokens = line.split()
                if len(tokens) == 7:
                    # TODO: This won't work with logins since they create new
                    # cookies, not just update existing ones.
                    host = tokens[0]
                    name = tokens[5]
                    value = tokens[6]
                    c.execute('''
                    UPDATE moz_cookies
                    SET value=?
                    WHERE baseDomain='neopets.com'
                      AND host=? AND name=?
                    ''', (value, host, name))
            cookies_db.commit()

        if 'templateLoginPopupIntercept' in self.content:
            print('Warning: Not logged in?')

        if 'randomEventDiv' in self.content:
            event = self.search(r'<div class="copy">(.*?)\t</div>')
            if event:
                event = strip_tags(event[1])
                print(f'[Random event: {event}]')
            else:
                print('[Random event]')

    def get_base(self, url, *params, **kwargs):
        if params or kwargs:
            url += '&' if '?' in url else '?'
            url += '&'.join(list(params) + dict_to_eq_pairs(kwargs))
        self.perform(url, [(pycurl.POST, 0)])

    def save_page(self, url, tag):
        parts = [x for x in url.split('/') if x]
        if not parts: parts = ['_']
        path_parts, filename = parts[:-1], parts[-1]
        path = '/'.join(['pages'] + path_parts)
        os.makedirs(path, exist_ok=True)
        time_ms = int(time.time() * 1000)
        self.last_file_path = f'{path}/{filename}_{tag}@{time_ms}'
        self.save_to_file(self.last_file_path)

    def get_url(self, url, *params, **kwargs):
        self.get_base(url, *params, **kwargs)
        self.save_page(url, 'get_url')

    def get(self, path, *params, **kwargs):
        self.get_base(self.base_url + path, *params, **kwargs)
        self.save_page(path, 'get')

    def post_base(self, url, *params, **kwargs):
        postfields = '&'.join(list(params) + dict_to_eq_pairs(kwargs))
        self.perform(url, [(pycurl.POST, 1), (pycurl.POSTFIELDS, postfields)])

    def post_url(self, url, *params, **kwargs):
        self.post_base(url, *params, **kwargs)
        self.save_page(url, 'post_url')

    def post(self, path, *params, **kwargs):
        self.post_base(self.base_url + path, *params, **kwargs)
        self.save_page(path, 'post')

    def find(self, *strings):
        loc = 0
        for string in strings:
            loc = self.content.find(string, loc)
        return loc

    def contains(self, string):
        return self.find(string) >= 0
    
    def search(self, regex):
        r = re.compile(regex, re.DOTALL)
        result = r.search(self.content)
        if not result:
            print(f'Warning: Search {regex} failed for page {self.last_file_path}')
        return result
    
    def findall(self, regex):
        r = re.compile(regex, re.DOTALL)
        return r.findall(self.content)
    
    def set_referer_path(self, path):
        self.referer = self.base_url + path

    def set_referer(self, url):
        self.referer = url
    
    def login(self, user, pwd):
        self.post('/login.phtml', f'username={user}&password={pwd}')
