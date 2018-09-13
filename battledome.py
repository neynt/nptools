import itertools
import json
import os
import re
import time

import lib

# TODO: Autodetect these.
PET_NAME = os.environ['PET_NAME']

path = '/dome/'
path_fight = '/dome/fight.phtml'
path_start_fight = '/dome/ajax/startFight.php'
path_arena = '/dome/arena.phtml'
path_arena_ajax = '/dome/ajax/arena.php'

def battledome(forever = False):
    np = lib.NeoPage(path)
    np.get(path_arena)
    neopoints_left = True
    prizes_left = True
    while prizes_left or forever:
        # Fights the Chia Clown on easy
        battle_id = None
        if np.contains('battleid:'):
            print('Battledome: Already in fight.')
            battle_id = np.search(r"battleid:'(\d+)',")[1]
        else:
            print('Battledome: Starting fight.')
            np.post(path_start_fight, 'type=2', f'pet={PET_NAME}', 'npcId=31', 'toughness=1')
            battle = json.loads(np.content)
            if not battle['success']:
                print('Battledome: Error.')
                return
            battle_id = battle['battle']['id']
        time.sleep(2)
        np.set_referer_path(path)
        np.get(path_arena)
        ts = int(time.time() * 1000)
        for step in itertools.count():
            intro = 1 if step == 0 else 0
            np.set_referer_path(path_arena)
            np.post(path_arena_ajax, f'battleid={battle_id}', f'step={step}', f'intro={intro}', 'status=1')
            resp = json.loads(np.content)
            abils = resp['p1']['abils']
            chosen_abil = ''
            for abil in ['14', '17', '10']:
                if abil in abils and not abils[abil]['hasCooldown']:
                    chosen_abil = abil
                    break
            items = re.findall(r'<li><img.*?id="(\d+)".*?title="(.*?)".*?/></li>', resp['p1']['items'])
            item1id = items[0][0]
            item2id = items[1][0]
            opts = []
            opts.append(f'p1s=')
            opts.append(f'eq1={item1id}')
            opts.append(f'eq2={item2id}')
            opts.append(f'p1a={chosen_abil}')
            opts.append(f'chat=')
            opts.append('action=attack')
            opts.append(f'ts={ts}')
            opts.append(f'battleid={battle_id}')
            opts.append(f'step={step}')
            opts.append(f'intro=0')
            opts.append('status=1')
            print(f'Battledome: Attacking with {items[0][1]} and {items[1][1]}')
            np.set_referer_path(path_arena)
            np.post(path_arena_ajax, *opts)
            resp = json.loads(np.content)
            if resp['battle']['prizes']:
                prizes = ', '.join(x['name'] for x in resp['battle']['prizes'])
                print(f'Battledome: Won {prizes}')
                if 'prize_messages' in resp['battle']:
                    prize_messages = resp['battle']['prize_messages']
                    if any('reached the item limit' in m for m in prize_messages):
                        prizes_left = False
                    if any('reached the NP limit' in m for m in prize_messages):
                        neopoints_left = False
                    print(f'Battledome: {prize_messages}')
                break

if __name__ == '__main__':
    battledome(True)
