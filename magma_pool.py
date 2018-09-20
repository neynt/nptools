import neotime
import lib

path = '/magma/pool.phtml'

def magma_pool():
    log = open('magma_pool.log', 'a')
    np = lib.NeoPage(path)
    np.get(path)
    now = neotime.now_nst()
    if np.contains("I'm sorry, only those well-versed"):
        print('Magma Pool: Not your time.')
        log.write(f'{now} NO\n')
    else:
        print(f'Magma Pool: {now} may be your time!!!')
        log.write(f'{now} YES\n')
    log.close()
