import atexit
from datetime import datetime, timedelta
import random
import re

import daemon
import lib
from lib import item_db
import lib.g as g
from lib import inventory
from lib import jellyneo

np = lib.NeoPage()
g.load_data()
#atexit.register(daemon.onexit)
