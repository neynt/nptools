from lib import inventory

def clean_inventory():
    inventory.quickstock(exclude=['Pant Devil Attractor'])

if __name__ == '__main__':
    clean_inventory()
