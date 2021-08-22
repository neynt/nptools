# nptools

Illicit automations for neopets.

**Note: I finally got frozen after autobuying 24/7 for about a month, so I won't be developing this anymore. Use at your own risk.**

## Features

- Daemon that you can just configure, run, and forget about
- Dailies, including difficult ones like Food Club (using max TER) and
  multi-dailies like underwater fishing
- Plays certain games very well. e.g. Shapeshifter, Fetch, Tyranu Evavu
- Restocks and prices items automatically ($$$)
- Logs certain results (e.g. lab zaps)
- Will probably get you frozen

## Quick start

Create a virtualenv and install requirements:

```shell
python -m venv venv
pip install -r requirements.txt
```

Put

```
NP_USER='username'
NP_PASS='password'
PET_NAME='name_of_your_pet'
```

in a file called .env in this directory.

Build the kvho shapeshifter solver with `cd c && ./build.sh`.

Then run `./run_daemon.sh`.

Additional env vars include `USER_AGENT` and `FIREFOX_COOKIES_DB`.

Best efforts were made to only have safe tasks are enabled in daemon.py; these
are the ones that can run on a brand new account. Look through the file and see
what you can safely uncomment.

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
