# NeoPage: Wrapper around pycurl that simulates a browser.
# TODO: Maybe eventually replace this with Selenium.

import io
import os
import pycurl
import re
import sqlite3
import time
from urllib.parse import urlsplit, urlencode, quote_plus

from . import util

class NotLoggedInError(Exception):
    pass

FIREFOX_COOKIES_DB = os.environ.get('FIREFOX_COOKIES_DB')
cookies_db = None
if FIREFOX_COOKIES_DB:
    cookies_db = sqlite3.connect(FIREFOX_COOKIES_DB)
USER_AGENT = os.environ.get('USER_AGENT', 'Mozilla/5.0')
COOKIE_FILE = 'nptools.cookies'

class NeoPage:
    def __init__(self, path=None, base_url=None):
        self.content = ''
        self.last_file_path = ''
        self.referer = ''
        self.base_url = base_url or 'http://www.neopets.com'
        if path:
            self.get(path)

    def save_to_file(self, filename):
        if type(self.content) == str:
            open(filename, 'w').write(self.content)
        elif type(self.content) == bytes:
            open(filename, 'wb').write(self.content)
        else:
            raise 'unknown content type'

    def load_file(self, filename):
        self.content = open(filename, 'r').read()

    def perform(self, url, opts=[]):
        storage = io.BytesIO()

        done_request = False
        for _ in range(5):
            try:
                storage.seek(0)
                storage.truncate(0)
                curl = pycurl.Curl()
                curl.setopt(pycurl.TIMEOUT_MS, 8000)
                curl.setopt(pycurl.FOLLOWLOCATION, True)
                curl.setopt(pycurl.REFERER, self.referer)
                curl.setopt(pycurl.WRITEFUNCTION, storage.write)
                if cookies_db:
                    host = '.'.join(self.base_url.rsplit('/', 1)[-1].split('.')[-2:])
                    c = cookies_db.cursor()
                    c.execute('''
                    SELECT name, value FROM moz_cookies
                    WHERE baseDomain = ?
                    AND expiry >= strftime('%s', 'now')
                    ''', (host,))
                    results = list(c.fetchall())
                    cookie_string = ';'.join(f'{name}={value}' for name, value in results)
                    curl.setopt(pycurl.COOKIE, cookie_string)
                else:
                    curl.setopt(pycurl.COOKIEFILE, COOKIE_FILE)
                curl.setopt(pycurl.COOKIEJAR, COOKIE_FILE)
                curl.setopt(pycurl.USERAGENT, USER_AGENT)
                curl.setopt(pycurl.URL, url)
                print(url)
                for k, v in opts:
                    curl.setopt(k, v)
                curl.perform()
                done_request = True
            except pycurl.error as e:
                print(f'pycurl error {e}')
                time.sleep(1)
            if done_request: break

        # Forces cookies to be flushed to COOKIE_FILE, I hope.
        del curl

        self.referer = url
        try:
            self.content = storage.getvalue().decode('utf-8')
        except UnicodeDecodeError:
            self.content = storage.getvalue()

        if cookies_db:
            c = cookies_db.cursor()
            for line in open(COOKIE_FILE).readlines():
                if line.startswith('#'): continue
                tokens = line.split()
                if len(tokens) == 7:
                    host = tokens[0]
                    path = tokens[2]
                    expiry = int(tokens[4])
                    name = tokens[5]
                    value = tokens[6]
                    c.execute('''
                    INSERT INTO moz_cookies (baseDomain, host, path, name, value, expiry)
                    VALUES ('neopets.com', ?, ?, ?, ?, ?)
                    ON CONFLICT (name, host, path, originAttributes)
                    DO UPDATE SET value=?, expiry=?
                    ''', (host, path, name, value, expiry
                        , value, expiry))
            cookies_db.commit()

        if type(self.content) == str:
            if 'templateLoginPopupIntercept' in self.content:
                print('Warning: Not logged in?')
            if 'randomEventDiv' in self.content:
                event = self.search(r'<div class="copy">(.*?)\t</div>')
                if event:
                    event = util.strip_tags(event[1])
                    print(f'[Random event: {event}]')
                else:
                    print('[Random event]')

    def get_base(self, url, *params, **kwargs):
        if params or kwargs:
            url += '&' if '?' in url else '?'
            url += '&'.join(list(list(params) + [urlencode(kwargs)]))
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
        postfields = '&'.join(list(params) + [urlencode(kwargs)])
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
