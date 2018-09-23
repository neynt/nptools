import sys
import lib

path = '/games/neoquest/neoquest.phtml'

# 1 2 3
# 4   5
# 6 7 8
movedir_cycle = [2,7]

def cycle(seed):
    while True:
        for elem in seed:
            yield elem

# Does not do all of Neoquest, unfortunately. Simply grinds by walking
# in a cycle.
def neoquest(once=False):
    np = lib.NeoPage(path)
    move_dirs = cycle(movedir_cycle)
    #?action=items
    #?action=items&useitemid=220000&do=use
    while True:
        hp_result = np.search(r'Health: <B>(\d+)</B>/(\d+)')
        hp = int(hp_result[1])
        hp_max = int(hp_result[2])
        print(f'Health: {hp}/{hp_max}')
        if np.contains('lupe_combat.gif'):
            moves = np.findall(r'''<A HREF="javascript:;" onClick="setdata\('(.*?)', (.*?)\); return false;">''')
            if hp_max - hp > 60 and ('special', '200019') in moves:
                np.post(path, 'fact=special', 'type=200019')
            elif hp < 80 and ('item', '220004') in moves:
                np.post(path, 'fact=item', 'type=220004')
            elif hp < 80 and ('item', '220003') in moves:
                np.post(path, 'fact=item', 'type=220003')
            elif hp < 80 and ('item', '220002') in moves:
                np.post(path, 'fact=item', 'type=220002')
            elif hp < 80 and ('item', '220001') in moves:
                np.post(path, 'fact=item', 'type=220001')
            elif ('special', '4003') in moves:
                np.post(path, 'fact=special', 'type=4003')
            elif ('attack', '0') in moves:
                np.post(path, 'fact=attack', 'type=0')
            else:
                np.post(path, 'fact=noop', 'type=0')
        elif np.contains('Leader Board'):
            if once: break
            if hp_max - hp > 80:
                np.get(path, 'action=items')
                if np.contains('220003&do=use'):
                    np.get(path, 'action=items', 'useitemid=220003', 'do=use')
                elif np.contains('220002&do=use'):
                    np.get(path, 'action=items', 'useitemid=220002', 'do=use')
                elif np.contains('220001&do=use'):
                    np.get(path, 'action=items', 'useitemid=220001', 'do=use')
                np.post(path)
            else:
                movedir = next(move_dirs)
                np.get(path, 'action=move', f'movedir={movedir}')
        elif np.contains('You are attacked by'):
            monster = np.search(r'You are attacked .*? <B>(.*?)</B>')[1]
            print(f'Fighting {monster}')
            np.post(path)
        elif np.contains('You defeated'):
            rewards = np.search(r'<CENTER><IMG SRC="http://images.neopets.com/nq/n/lupe_win.gif">(.*?)</CENTER>')[1]
            rewards = lib.strip_tags(rewards)
            print(rewards)
            np.post(path, 'end_fight=1')
        else:
            print("I don't know how to handle this.")
            break

if __name__ == '__main__':
    neoquest('once' in sys.argv)
