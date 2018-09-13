import lib
import datetime
import neotime

path = '/winter/snowager.phtml'
path2 = '/winter/snowager2.phtml'

def snowager():
    dont_do_again = neotime.now_nst() + datetime.timedelta(hours=1)
    np = lib.NeoPage(path)
    if np.contains('The Snowager is awake'):
        print('Snowager: Awake.')
        return
    np.get(path2)
    if np.contains('You dont want to try and enter again'):
        print('Snowager: Already done.')
        return dont_do_again
    result = np.search(r'<p>(.*?)<p></center><center>')
    if result:
        result = lib.strip_tags(result[1])
        print(f'Snowager: {result}')
        return dont_do_again
    else:
        print('Snowager: Error.')

if __name__ == '__main__':
    snowager()
