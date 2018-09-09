#!/usr/bin/env python3

import datetime
import re

import lib
import neotime

path = '/pirates/academy.phtml'

# Goal: Trains your pet at the pirate academy, prioritizing skills in this
# order, and trying to keep all skills level: Str, Def, Hp, Mov, Lvl

# Subgoals:
# - Trains level if necessary (some skill is over twice level)
# - Obtains a dubloon if necessary
#   - Searches shop wizard several times
#   - Obtains NP from bank if necessary
# - Integrate with daemon (dynamic next times)

def pirate_academy():
    np = lib.NeoPage()
    np.get(path, 'type=status')
    # TODO: Handle more than one pet, train particular pet, etc.
    table = np.search(r'<b>Current Course Status</b>.*?<table.*?>.*?<br clear="all">')[0]
    tds = re.findall(r'<td.*?>(.*?)</td>', table)
    status = tds[0]
    stats = tds[1].split('<br>')
    stats = [re.sub(r'<.*?>', '', s).split()[-1] for s in stats[1:-2] if s]
    Lvl, Str, Def, Mov, Hp = map(int, stats)
    time_til = tds[2]

    if 'Course Finished!' in time_til:
        pet_name = np.search(r"<form.*?name='pet_name' value='(.*?)'.*?</form>")[1]
        np.post('/pirates/process_academy.phtml', 'type=complete', f'pet_name={pet_name}')
        result = lib.strip_tags(np.content.splitlines()[-1])
        print(f'Pirate Academy: Finished course. {result}')
        return pirate_academy()

    elif 'is not on a course' in status:
        np.get(path, 'type=courses')
        r = np.search(r"<select name='pet_name'><option value='(.*?)'>.*? - (.*?)</select>")
        pet_name = r[1]
        rank = r[2]
        skill = None
        if any(stat > 2 * Lvl for stat in [Str, Def, Mov, Hp]):
            skill = 'Level'
        else:
            skill = min(zip([Str, Hp, Def, Mov], ('Strength', 'Endurance', 'Defence', 'Agility')), key=lambda x:x[0])[1]
        print(f'Pirate Academy: Training {skill} for {pet_name}')
        np.post('/pirates/process_academy.phtml', 'type=start', f'course_type={skill}', f'pet_name={pet_name}')
        return pirate_academy()

    elif "<input type='submit' value='Pay'>" in np.content:
        print(f'Pirate Academy: Paying for lesson')
        pet_name = np.search(f"<input type='hidden' name='pet_name' value='(.*?)'>")[1]
        np.post('/pirates/process_academy.phtml', f'pet_name={pet_name}', 'type=pay')

    print(f'Status: {lib.strip_tags(status)}')
    print(f'Stats: Lvl{Lvl} Str{Str} Def{Def} Mov{Mov} Hp{Hp}')
    print(time_til)
    total_time = datetime.timedelta()
    result = np.search('(\d+) hr')[1]
    if result: total_time += datetime.timedelta(hours=int(result))
    result = np.search('(\d+) minute')[1]
    if result: total_time += datetime.timedelta(minutes=int(result))
    result = np.search('(\d+) second')[1]
    if result: total_time += datetime.timedelta(seconds=int(result))
    print(f'Time til: {total_time}')
    return neotime.now_nst() + total_time + datetime.timedelta(minutes=1)

if __name__ == '__main__':
    pirate_academy()
