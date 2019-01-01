import datetime
import os
import re

import lib
from lib import neotime
from lib import inventory

# Goal: Trains your pet at the pirate academy, prioritizing skills in this
# order, and trying to keep all skills level: Str, Def, Hp, Mov, Lvl

# Subgoals:
# - Trains level if necessary (some skill is over twice level)
# - Obtains a dubloon if necessary
#   - Searches shop wizard several times
#   - Obtains NP from bank if necessary
# - Integrate with daemon (dynamic next times)

def base_academy(path, path_process):
    np = lib.NeoPage()
    np.get(path, 'type=status')

    table = np.search(r'<b>Current Course Status</b>.*?<table.*?>.*?<br clear="all">')[0]
    trs = re.findall(r'<tr>(.*?)</tr>', table)

    finish_times = []
    for tr1, tr2 in zip(trs[::2], trs[1::2]):
        pet_name, status = re.search(r'<b>(.*?) \(Level \d+\) is (.*?)</b>', tr1).group(1, 2)
        print(f'{pet_name}: {status}')
        Lvl, Str, Def, Mov, Hp = [int(lib.strip_tags(x).split()[-1]) for x in tr2.split('<br>')[1:6]]

        if 'Time till course finishes' in tr2:
            finish_time = datetime.timedelta()
            if np.contains('hr'):
                result = np.search('(\d+) hr')
                if result: finish_time += datetime.timedelta(hours=int(result[1]))
            if np.contains('minute'):
                result = np.search('(\d+) minute')
                if result: finish_time += datetime.timedelta(minutes=int(result[1]))
            if np.contains('second'):
                result = np.search('(\d+) second')
                if result: finish_time += datetime.timedelta(seconds=int(result[1]))
            finish_times.append(finish_time)
            continue

        # Only train pet specified by PET_NAME.
        if pet_name != os.environ.get('PET_NAME'): continue

        # Complete any course that's done.
        if 'Complete Course!' in tr2:
            np.post(path_process, 'type=complete', f'pet_name={pet_name}')
            result = lib.strip_tags(np.content.splitlines()[-1])
            print(f'Finished course for {pet_name}. {result}')

        want_money_indicators = [
            "<input type='hidden' name='type' value='pay'>",
            'has not been paid for yet',
        ]
        if any(x in tr2 for x in want_money_indicators):
            # Pay for current course.
            np.get(path)
            items = re.findall('<b>([\w \-]+?)</b><img', tr2)
            for item in items:
                inventory.withdraw_sdb(item)
            np.post(path_process, f'pet_name={pet_name}', 'type=pay')
        else:
            # Start a new course
            np.get(path, 'type=courses')
            # TODO: Take advantage of island training school's endurance to 3x health feature.
            skill = None
            if any(stat > 2 * Lvl for stat in [Str, Def, Mov, Hp]):
                # Train level if we must.
                skill = 'Level'
            else:
                # Otherwise, train the lowest skill.
                skill = min(zip([Str, Hp, Def, Mov], ('Strength', 'Endurance', 'Defence', 'Agility')), key=lambda x:x[0])[1]
            print(f'Training {skill} for {pet_name}')
            np.post(path_process, 'type=start', f'course_type={skill}', f'pet_name={pet_name}')

    if len(finish_times) == 0:
        return base_academy(path, path_process)
    else:
        return neotime.now_nst() + min(finish_times) + datetime.timedelta(minutes=1)

def pirate_academy():
    path = '/pirates/academy.phtml'
    path_process = '/pirates/process_academy.phtml'
    return base_academy(path, path_process)

def island_training():
    path = '/island/training.phtml'
    path_process = '/island/process_training.phtml'
    return base_academy(path, path_process)

if __name__ == '__main__':
    #print(pirate_academy())
    island_training()
    #inventory.withdraw_sdb('Vo Codestone')
