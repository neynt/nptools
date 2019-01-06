from lib import inventory
import sys

if __name__ == '__main__':
    # TODO: selects a random item if multiple of those items exist... which may
    # be bad
    item_name = sys.argv[1]
    quantity = 1 if len(sys.argv) <= 2 else int(sys.argv[2])
    inventory.purchase(item_name, quantity=quantity, laxness=3)
