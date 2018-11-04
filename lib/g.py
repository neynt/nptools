# Global state for hacks and persisting not-super-important shared data among
# multiple activities.
import os
import pickle
import shutil
from datetime import datetime, timedelta

from collections import defaultdict

class TTLCache:
    def __init__(self, ttl, data=None):
        self.data = {}
        self.insert_time = {}
        self.ttl = ttl
        if self.data:
            for k, v in self.data.items():
                self.put(k, v)

    def put(self, key, value):
        self.data[key] = value
        self.insert_time[key] = datetime.utcnow()

    def get(self, key):
        if key not in self.insert_time:
            return None
        if self.insert_time[key] + self.ttl < datetime.utcnow():
            del self.data[key]
            del self.insert_time[key]
            return None
        else:
            return self.data[key]

    def keys(self):
        for key in list(self.data.keys()):
            if self.get(key) != None:
                yield key

    def values(self):
        for key in self.keys():
            yield self.get(key)

    def items(self):
        for key in self.keys():
            yield key, self.get(key)

    def __len__(self):
        return len(list(self.keys()))

    __setitem__ = put
    __getitem__ = get

    def __repr__(self):
        return 'TTLCache({}, {{{}}})'.format(
            self.ttl,
            ', '.join(f'{k}: {v}' for k, v in self.items()),
        )
    __str__ = __repr__

PICKLE_FILE = 'g.pickle'

global_variables = [
    'last_done',
    'items_stocked',
    'consec_empty_shops',
    'markets',
    'level2_cache',
    'last_ban',
]

transform = {
    'markets': dict,
}

untransform = {
    'markets': lambda d: defaultdict(lambda: TTLCache(timedelta(hours=1)), d),
}

last_done = {}
items_stocked = defaultdict(int)
consec_empty_shops = 0
markets = defaultdict(lambda: TTLCache(timedelta(hours=1)))
level2_cache = TTLCache(timedelta(hours=1))
last_ban = None

def load_data():
    if os.path.isfile(PICKLE_FILE):
        data = pickle.load(open(PICKLE_FILE, 'rb'))
        g = globals()
        for v in global_variables:
            g[v] = untransform.get(v, lambda x:x)(data.get(v, g[v]))

def save_data():
    g = globals()
    pickle.dump({v: transform.get(v, lambda x:x)(g[v]) for v in global_variables}, open(PICKLE_FILE, 'wb'))
    # Backup copy will only be made if pickle succeeds.
    shutil.copyfile(PICKLE_FILE, f'{PICKLE_FILE}.bak')
    print(f'Pickle success. Backup saved at {PICKLE_FILE}.bak')
