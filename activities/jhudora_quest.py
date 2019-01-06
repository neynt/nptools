import lib
import os
import datetime
from lib import neotime, NeoPage

path = '/faerieland/darkfaerie.phtml'
path_process = '/faerieland/process_darkfaerie.phtml'

def jhudora_quest():
    np = NeoPage(save_pages=True)
    np.get(path)

    if 'I Accept!' in np.content:
        user = os.environ['NP_USER']
        np.post(path_process, 'type=accept', f'username={user}')

if __name__ == '__main__':
    jhudora_quest()
