import lib

path = '/shop_of_offers.phtml'

def rich_slorg():
    np = lib.NeoPage(path)
    if np.contains('slorg_payout=yes'):
        np.get(path, 'slorg_payout=yes')
        prize = np.search(r'You have received <strong>(.*?)</strong>')[1]
        print(f'Rich slorg: Got {prize}')
    else:
        print('Rich slorg: Could not find.')

if __name__ == '__main__':
    rich_slorg()
