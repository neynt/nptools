#!/usr/bin/python2

import StringIO
import re
import pycurl

import NeoPage

page = NeoPage.NeoPage()

def print_title(title):
	print('')
	print("========" + "="*len(title))
	print("||  " + title + "  ||")
	print("========" + "="*len(title))

def d_anchormanagement():
	print_title("Anchor Management")
	url = '/pirates/anchormanagement.phtml'
	page.req(url)
	if page.has('id="form-fire-cannon"') is False:
		print("Error!")
		return
	hsh = page.juice('form-fire-cannon(.*?)value="(.*?)"></form>', 2)
	page.req(url, 'action='+hsh)
	prize = page.juice('prize-item-name">(.*?)</span>')
	if prize:
		print("Blasted krawken, got " + prize)
	elif page.has("you've already done your share"):
		print("Already blasted the krawken today.")
	else:
		print("Blasted krawken, indeterminate prize")

def d_applebobbing():
	print_title("Apple Bobbing")
	page.req('/halloween/applebobbing.phtml?bobbing=1')
	if page.has('hf_call_to_action') is False:
		print("Error!")
		return
	else:
		prize = page.juice('hf_call_to_action(.*?)<br><br>\n\n(.*?)\t</div>', 2)
		print("Got " + prize)
		return

def d_bankinterest():
	print_title("Bank Interest")
	page.req('/bank.phtml')
	prize = page.juice(r'Collect Interest \((.*?)\)')
	if prize:
		page.req('/process_bank.phtml', 'type=interest')
		print("Collecting " + prize)
	elif page.has('You have already collected your interest today.'):
		print("Already collected interest today.")
	else:
		print("Error!")

def d_councilchamber():
	print_title("Council Chamber")
	url = '/altador/council.phtml';
	page.req(url)
	prhv = page.juice(r'\?prhv=(.*?)">')
	if prhv is False:
		print("Problem with getting prhv.")
		return
	page.req(url, 'prhv='+prhv+'&collect=1')
	prize = page.juice(r'King Altador hands you your gift(.*?)<B>(.*?)</B>', 2)
	if prize:
		print("Problem with retrieving gift.")
		return
	elif page.has("already received your free prize today"):
		print("""King Altador frowns at you as you enter. "You've already received your free prize today. I'd like to think you can summon the patience to wait again until tomorrow.""")
	else:
		print("Got " + prize)

def d_fishing():
	print_title("Underwater Fishing")
	page.req('/water/fishing.phtml', 'go_fish=1')
	prize = page.juice(r'You reel in your line and get...(.*?)<B>(.*?)</B>', 2)
	if prize:
		print("You reel in your line and get... " + prize)
	else:
		print("Error!")

# Needs prize ident and collect
def d_forgottenshore():
	print_title("Forgotten Shore")
	page.req('/pirates/forgottenshore.phtml')
	if page.has('nothing of interest to be found today.'):
		print("Nothing of interest.")
	else:
		print("Has something! Check it out some time.")

# Needs prize output
def d_fruitmachine():
	print_title("Fruit Machine")
	page.req('/desert/fruitmachine2.phtml')
	if page.has("You have already played"):
		print("Already played.")

def d_omelette():
	print_title("Omelette")
	page.req('/prehistoric/omelette.phtml', 'type=get_omelette')
	if page.has("You cannot take more than one slice per day!"):
		print("Already done today.")
	elif page.has("You approach"):
		win = page.juice("items/(.*?)' width=")
		print("Got " + win)
	else:
		print("Error!")

def d_jelly():
	print_title('Giant Jelly')
	page.req('/jelly/jelly.phtml', 'type=get_jelly')
	prize = page.juice(r'You take some <b>(.*?)</b>')
	if prize:
		print("Got " + prize)
	elif page.has("You cannot take more than one jelly per day!"):
		print("Already done today.")
	else:
		print("Error!")

def d_lunartemple():
	print_title('Shenkuu Lunar Temple')
	page.req('/shenkuu/lunar/?show=puzzle')
	k = page.juice('angleKreludor=(.*?)&')
	if k is False:
		print("Dunno man, didn't give me an angle.")
		return
	angle = str(int(((int(k)+191)%360)/22.5))
	print("Moon phase " + angle)
	page.req('/shenkuu/lunar/results.phtml', 'submitted=true&phase_choice='+angle)
	prize = page.juice(r".com/items/(.*?)' border")
	if prize:
		print("Got item with img " + prize)
	elif page.has("You may only answer the challenge once per day."):
		print("Already done.")
	else:
		print("Error!")

def d_plushie():
	print_title('The DMBGP of Prosperity')
	page.req('/faerieland/tdmbgpop.phtml', 'talkto=1')
	prize = page.juice(r"<div align='center'>(.*?)</div>")
	if prize:
		print(prize)
	elif page.has("You have already visited the plushie today"):
		print("Already visited.")
	else:
		print("Couldn't find plushie! Or other error.")

def d_richslorg():
	print_title('Rich Slorg')
	page.req('/shop_of_offers.phtml?slorg_payout=yes')
	prize = page.juice(r"You have received <strong>(.*?)</strong>")
	if prize:
		print(prize)
	elif page.has("<b>click on them</b>"):
		print("Already done.")
	else:
		print("Could not find! Or other error.")

# HIGHLY INCOMPLETE OUTPUT (but probably functional)
def d_tomb():
	print_title('Deserted Tomb')
	page.req('/worlds/geraptiku/process_tomb.phtml',
		referer='http://www.neopets.com/worlds/geraptiku/tomb.phtml')
	text = page.juice(r'<strong>Deserted Tomb</strong>(.*?)<center>')
	print(text)

# Needs prettier output
def d_tombola():
	print_title('Tombola')
	page.req('/island/tombola2.phtml', referer='/island/tombola.phtml')
	text = page.juice(r'<div style="width: 635px;"><center>(.*?)<input')
	if text:
		print(text)
	elif page.has("Sorry, you are only allowed one Tombola free spin every day"):
		print("Sorry, you are only allowed one Tombola free spin every day")
	else:
		print("Error")

def d_toychest():
	print_title('Toy Chest')
	page.req('/petpetpark/daily.phtml', 'go=1')
	item_prize = page.juice('prize-item-name">(.*?)</span>')
	np_prize = page.juice('<BR><BR><B>(.*?)</B>')
	if item_prize:
		print("Won item: " + item_prize)
	elif np_prize:
		print("Won " + np_prize)
	elif page.has("already collected your prize today."):
		print("Already collected prize today.")
	else:
		print("Did not win any prize somehow! Error?")

def do_dailies():
	d_anchormanagement()
	d_applebobbing()
	d_bankinterest()
	d_councilchamber()
	d_fishing()
	d_forgottenshore()
	d_fruitmachine()
	d_jelly()
	d_lunartemple()
	d_omelette()
	d_plushie()
	d_richslorg()
	d_tomb()
	d_tombola()
	d_toychest()

def login(user, pwd):
	page.req('/login.phtml', 'username='+user+'&password='+pwd)
