import lib

def lab_ray():
    log = open('lab_ray.log', 'a')
    np = lib.NeoPage('/lab.phtml')
    np.post('/lab2.phtml', 'donation=100')
    pet_name = np.active_pet_name()
    np.post('/process_lab2.phtml', f'chosen={pet_name}')
    if np.contains('You can only use the lab once a day'):
        print(f'Lab ray: Already fired.')
        return
    result = lib.strip_tags(np.search(r'''The ray is fired (.*?)<FORM action="/lab.phtml">''')[1])
    print(f'Lab ray: The ray is fired {result}')
    log.write(result + '\n')

if __name__ == '__main__':
    lab_ray()
