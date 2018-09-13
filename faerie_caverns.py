#!/usr/bin/env python3
import lib

path = '/faerieland/caverns/index.phtml'

def faerie_caverns():
    np = lib.NeoPage(path)
    if np.contains('already visited today'):
        print('Already did faerie caverns.')
    else:
        lib.inv.ensure_np(400)
        while True:
            np.post(path, 'play=1')
            if np.contains('caverns/faerie_cave'):
                if np.contains('faerie_cave_dead_end.gif'):
                    print("Dead end!")
                    break
                elif np.contains("Click to see what you've found"):
                    continue
                elif np.contains('faerie_cave_success.gif'):
                    print("Won!")
                    break
                else:
                    print("In the Faerie Caverns...")
            else:
                print("Couldn't find faerie caverns.")
                break

if __name__ == '__main__':
    faerie_caverns()
