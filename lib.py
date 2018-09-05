import io
import pycurl
import re
import time

def dict_to_eq_pairs(kwargs):
    return [f'{k}={v}' for k, v in kwargs.items()]

class NotLoggedInError(Exception):
    pass

class NeoPage:
    def __init__(self, path=None, user_agent='Mozilla/5.0'):
        self.storage = io.BytesIO()
        self.content = ''
        self.base_url = 'http://www.neopets.com'
        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.WRITEFUNCTION, self.storage.write)
        self.curl.setopt(pycurl.COOKIEFILE, 'nptools.cookies')
        self.curl.setopt(pycurl.COOKIEJAR, 'nptools.cookies')
        self.curl.setopt(pycurl.USERAGENT, user_agent)
        if path:
            self.get(path)

    def save_to_file(self, filename):
        open(filename, 'w').write(self.content)

    def load_file(self, filename):
        self.content = open(filename, 'r').read()

    def perform(self, url):
        self.curl.setopt(pycurl.URL, url)
        self.storage.seek(0)
        self.storage.truncate(0)
        self.curl.perform()
        self.content = self.storage.getvalue().decode('utf-8')
        self.curl.setopt(pycurl.REFERER, url)
        if 'templateLoginPopupIntercept' in self.content:
            print('Warning: Not logged in?')

    def get_base(self, url, *params, **kwargs):
        if params or kwargs:
            url += '&' if '?' in url else '?'
            url += '&'.join(list(params) + dict_to_eq_pairs(kwargs))
        self.curl.setopt(pycurl.POST, 0)
        self.perform(url)

    def save_page(self, url, tag):
        url = url.replace('/', '_')
        time_ms = int(time.time() * 1000)
        self.save_to_file(f'pages/{url}_{tag}@{time_ms}')

    def get_url(self, url, *params, **kwargs):
        self.get_base(url, *params, **kwargs)
        self.save_page(url, 'get_url')

    def get(self, path, *params, **kwargs):
        self.get_base(self.base_url + path, *params, **kwargs)
        self.save_page(path, 'get')

    def post_base(self, url, *params, **kwargs):
        postfields = '&'.join(list(params) + dict_to_eq_pairs(kwargs))
        self.curl.setopt(pycurl.POST, 1)
        self.curl.setopt(pycurl.POSTFIELDS, postfields)
        self.perform(url)

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
        return r.search(self.content)
    
    def findall(self, regex):
        r = re.compile(regex, re.DOTALL)
        return r.findall(self.content)
    
    def set_referer_path(self, path):
        self.curl.setopt(pycurl.REFERER, self.base_url + path)

    def set_referer(self, url):
        self.curl.setopt(pycurl.REFERER, url)
    
    def login(self, user, pwd):
        self.post('/login.phtml', f'username={user}&password={pwd}')
