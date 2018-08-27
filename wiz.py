#!/usr/bin/python2

import sys
import sqlite3
from neo import *
import itemdb

name = sys.argv[1]
itemdb.update_item_worth(name)
