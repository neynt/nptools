import json
import lib

def kiko_pop():
    np = lib.NeoPage('/worlds/kiko/kpop/')
    # TODO: different difficulty?
    np.post('/worlds/kiko/kpop/ajax/difficulty.php', 'difficulty=2')
    print(np.content)
    result = json.loads(np.content)
    if not result['success']:
        print(f'Kiko Pop: Already done today.')
        return

    np.post('/worlds/kiko/kpop/ajax/prize.php', 'difficulty=2')
    print(f'Kiko Pop: {np.content}')
    result = json.loads(np.content)

if __name__ == '__main__':
    kiko_pop()
