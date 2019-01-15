import lib
import os
import datetime
from lib import neotime, NeoPage, inventory
import re

path = '/faerieland/darkfaerie.phtml'
path_process = '/faerieland/process_darkfaerie.phtml'

def jhudora_quest():
    np = NeoPage(save_pages=True)
    np.get(path)

    if 'I Accept!' in np.content:
        # TODO: Search your SDB, gallery, shop, and Neohome Superstore for item as well.
        user = os.environ['NP_USER']
        np.post(path_process, 'type=accept', f'username={user}')
        m = re.search(r"<br>Where is my <b>(.*?)</b>\?<p><img src='http://images.neopets.com/items/(.*?)'.*?>", np.content)
        item = m[1]
        image = m[2]
        print(f'Jhudora asked for {item} ({image})')
        cost = inventory.purchase(item, image=image)
        print(f'Bought it for {cost} NP.')
        np.set_referer_path(path)
        np.post(path_process, 'type=finished')
        if 'You have completed' in np.content:
            print(f'Quest shouuuuld be completed?')
        else:
            print(f"Quest doesn't seem to have completed")
    elif 'I am not ready' in np.content:
        print("Too early for Jhudora's Quest.")
    else:
        print("Jhudora's quest: Error!")

if __name__ == '__main__':
    jhudora_quest()
