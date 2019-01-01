from lib import NeoPage
import random
from urllib.parse import parse_qs

base_url = 'http://ncmall.neopets.com'
path = '/mall/shop.phtml?page=giveaway'

def expellibox():
    np = NeoPage(base_url=base_url)
    np.get(path)
    rand = random.randint(1, 99999)
    np.post(f'/games/giveaway/process_giveaway.phtml?r=rand', 'onData=[type Function]')
    log = open('expellibox.log', 'a')
    result = parse_qs(np.content)
    success = result['success']
    prize_id = result['prize_id']
    msg = result['msg']
    print(rand, result)
    log.write(f'{rand},{result}\n')

if __name__ == '__main__':
    expellibox()
