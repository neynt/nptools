# nptools

Illicit automations for neopets.

## Quick start

Put

```
NP_USER='username'
NP_PASS='password'
PET_NAME='xX_bestpet_Xx
```

in a file called .env in this directory. Then run `./run.sh daemon.py`.

Additional flags include `USER_AGENT` and `FIREFOX_COOKIES_DB`.

A lot of this code was written with assumptions that only hold true on my
account (e.g. you only have one pet, for training). So run it at your own risk
and maybe start the daemon with only a few safe dailies enabled first.

Produced files include:

```
itemdb.db: sqlite3 database of Neopets items.
daemon.pickle: pickled dict from daily name to when you last did them.
nptools.cookies: cookies from curl.
*.log: various activity-specific log files.
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

- Food club (depends on age of account; avg. 30-50k/day)
- Negg Cave (interesting puzzle)
- Wishing Well (small chance of 300k-600k)
- Sakhmet Solitaire (5k/day)
- Cliffhanger (1500 NP/day)
- Scarab 21 (5k/day)
- Grave Danger
- NeoQuest II
- Cheat
- Sewage Surfer
- Shapeshifter
- Go go go
- Godori
- Krawps
- Wheels
- Neggsweeper (3k/day)
- NeoPoker
  - full house: 100NP
- Turmaculus
- Monthly freebies: http://www.neopets.com/freebies/index.phtml
- Potato counter
- Meteor crash site
- Guess the weight of the marrow
- Scorchy Slots (map pieces?)
- Symol Hole
- Island mystic (until avatar)
- Quests
- Mystery pic (really interesting automation problem)
- Lottery (avatar, and slightly +EV (more if you pick numbers other people don't))
- Fetch (maze solving with hidden information)
- Qasalan Expellibox (chance of NC every 8 hours)
