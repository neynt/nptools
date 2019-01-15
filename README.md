# nptools

Illicit automations for neopets.

## Features

- Daemon that you can just configure, run, and forget about
- Dailies, including difficult ones like Food Club (using max TER) and
  multi-dailies like underwater fishing
- Plays certain games very well. e.g. Shapeshifter, Fetch, Tyranu Evavu
- Restocks and prices items automatically ($$$)
- Logs certain results (e.g. lab zaps)
- Will probably get you frozen

## Quick start

Put

```
NP_USER='username'
NP_PASS='password'
PET_NAME='xX_bestpet_Xx'
```

in a file called .env in this directory. Then run `./run_daemon.sh`.

Additional flags include `USER_AGENT` and `FIREFOX_COOKIES_DB`.

A lot of this code was written with assumptions that only hold true on my
account. So run it at your own risk and maybe start the daemon with only a few
safe dailies enabled first. (Comment out most of the tasks in daemon.py)

## Produced files

```
itemdb.db: sqlite3 database of Neopets items.
g.pickle: pickle of some state we want to persist (see `lib/g.py`).
nptools.cookies: cookies from curl.
*.log: various activity-specific log files. e.g. lab_ray.log tracks zap results.
pages/: copies of all requested pages.
shop_captchas/: images of captchas when buying items.
```

## Directory structure

- `lib/`: Base library with shared functionality.
- `activities/`: Application of lib to specific activities around the site.
- `repl.py`: Imports a bunch of things for `python -i` use.
- `daemon.py`: Does activities at regular intervals you specify.

## TODO

### Site activities

- Negg Cave (interesting puzzle)
- Wishing Well (small chance of 300k-600k, probably +ev?)
- Sakhmet Solitaire (5k/day)
- Scarab 21 (5k/day)
- Neggsweeper (3k/day)
- Cliffhanger (1500 NP/day)
- Grave Danger
- NeoQuest II
- Cheat
- Sewage Surfer
- Go go go
- Godori
- Krawps
- Wheels (requires AWF)
- NeoPoker
- Turmaculus
- Monthly freebies: http://www.neopets.com/freebies/index.phtml
- Potato counter
- Meteor crash site
- Guess the weight of the marrow
- Scorchy Slots (map pieces?)
- Symol Hole
- Island mystic (until avatar)
- Quests
  - Illusen
  - Jhudora
  - Kitchen
  - Edna
  - Brain Tree
  - Esophagor
  - Taelia
  - Coincidence
- Mystery pic (really interesting scraping, vision problem)
- Scratchcard scratching
