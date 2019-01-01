from lib import NeoPage

path = '/games/slots.phtml'

def scorchy_slots():
    np = NeoPage()
    np.get(path)
    _ref_ck = np.search(r"<input type='hidden' name='_ref_ck' value='(.*?)'>")[1]
    np.post(path, f'_ref_ck={_ref_ck}', 'play=yes')

    while True:
