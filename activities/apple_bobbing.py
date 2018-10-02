from lib import NeoPage
from lib.util import strip_tags

path = '/halloween/applebobbing.phtml'

def apple_bobbing():
    np = NeoPage(path)
    if np.contains('Give it a shot!'):
        np.get(path, bobbing=1)
        message = np.search("<div id='bob_middle'>(.*?)</div>")[1].strip()
        message = strip_tags(message)
        print(message)
    elif np.contains('blind underneath this hat'):
        print('Already apple bobbed today.')
    else:
        print("Couldn't find apple bobbing.")

if __name__ == '__main__':
    apple_bobbing()
