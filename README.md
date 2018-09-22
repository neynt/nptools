# nptools

illicit automations for neopets.

## Quick start

Put

```
NP_USER='username'
NP_PASS='password'
```

in a file called .env in this directory. Then run `./daemon.sh`.

## TODO

### Technical

- Read (and write??) cookies from (and to???) an actual browser. Chrome stores
  cookies in an sqlite database so this should actually be quite doable.
  - Update: It's encrypted so maybe it's not super easy.
- Maintain our own item database with prices using the shop wizard

### Site activities

- Food club (depends on age of account; avg. 30-50k/day)
- Negg Cave (interesting puzzle)
- Wishing Well (small chance of 300k-600k)
- Sakhmet Solitaire (5k/day)
- Faerieland jobs (~5-10k/day)
- Cliffhanger (1500 NP/day)
- Scarab 21 (5k/day)
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
- Restocking
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
