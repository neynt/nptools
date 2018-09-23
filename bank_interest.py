import lib

def bank_interest():
    path = '/bank.phtml'
    np = lib.NeoPage(path)
    if np.contains('You have already collected your interest today.'):
        print('Already collected interest today.')
    elif np.contains('Collect Interest ('):
        amount = np.search(r'Collect Interest \((.*?)\)')[1]
        print(f"Collecting {amount} interest.")
        np.post('/process_bank.phtml', 'type=interest')
    else:
        print("Error collecting bank interest.")

if __name__ == '__main__':
    bank_interest()
