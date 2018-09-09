#!/usr/bin/env python3
import datetime
import random

# Current Neopian standard time.
def now_nst():
    t = datetime.datetime.utcnow()
    t -= datetime.timedelta(hours=7)
    return t

def next_day_at(**kwargs):
    def f(last_time):
        next_time = last_time + datetime.timedelta(days=1)
        return next_time.replace(**kwargs)
    return f

# Dailies with priority. Low-idx dailies are completed first.
# Equal-idx dailies are completed in an arbitrary order.
def daily(idx):
    return next_day_at(hour=4, minute=idx, second=random.randint(0, 59))

def after(**kwargs):
    def f(last_time: datetime.datetime):
        return last_time + datetime.timedelta(**kwargs)
    return f

def immediate(last_time):
    return last_time

def snowager_time(last_time_):
    now = now_nst()
    if now.time() < datetime.time(7, 0, 0):
        return now.replace(hour=6, minute=1, second=0)
    elif now.time() < datetime.time(15, 0, 0):
        return now.replace(hour=14, minute=1, second=0)
    elif now.time() < datetime.time(23, 0, 0):
        return now.replace(hour=22, minute=1, second=0)
    else:
        now += datetime.timedelta(days=1)
        return now.replace(hour=6, minute=1, second=0)

