#!/usr/bin/env python3
import datetime
import random

# Current Neopian standard time.
def now_nst():
    t = datetime.datetime.utcnow()
    # TODO: Daylight savings time
    t -= datetime.timedelta(hours=8)
    return t

def next_day_at(**kwargs):
    def f(last_time):
        next_time = last_time + datetime.timedelta(days=1)
        return next_time.replace(**kwargs)
    return f

def next_hour_at(**kwargs):
    def f(last_time):
        next_time = last_time + datetime.timedelta(hours=1)
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

def next_snowager_time(last_time):
    now = now_nst()
    if last_time.time() < datetime.time(7, 0, 0):
        return last_time.replace(hour=6, minute=1, second=0)
    elif last_time.time() < datetime.time(15, 0, 0):
        return last_time.replace(hour=14, minute=1, second=0)
    elif last_time.time() < datetime.time(23, 0, 0):
        return last_time.replace(hour=22, minute=1, second=0)
    else:
        now += datetime.timedelta(days=1)
        return now.replace(hour=6, minute=1, second=0)

# Transforms an existing next-timer by skipping King Skarl's lunchtime.
def skip_lunch(f):
    lunch_hours = [8, 13, 19]
    def g(last_time: datetime.datetime):
        next_time = f(last_time)
        next_time = max(next_time, now_nst())
        for h in lunch_hours:
            if datetime.time(h-1, 59, 0) <= next_time.time() <= datetime.time(h+1, 0, 0):
                return next_time.replace(hour=h+1, minute=1, second=0)
        return next_time
    return g
