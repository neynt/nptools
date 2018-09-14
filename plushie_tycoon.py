#!/usr/bin/env python3
import re

import lib

# Important facts
# - The flow of a plushie is materials→factory→warehouse→store
# - Weekly rent is:
#   - 980 per factory level
#   - 940 per warehouse level
#   - 1350 per store level
# - You can hold 100 materials up to 150k COH; 250 after that.
# - A factory of size s lets you work on 2s jobs at once.
# - A warehouse of size 10-s loads j jobs in 20s + 2js minutes.
# - A store of size s lets you sell 400s plushies at once (9 is unlimited)
# - 5 minutes shipping from warehouse to store.

# Variable costs are:
# - Materials
# - Labour (sort of)
# - Shipping (278 NP / 100 plushies)

# Wisdom from player guides:
# - first 3 levels of first 3 upgrades and first 4 adverts is a good starting
# point for your store
# - should only bother with species of at least 4 cloth
# - other than cloth, not worth using anything but the priciest materials
#   - we will start by varying only species; then maybe see effect of different
#   cloths.

# Bottlenecks:
# - Store has plushie limit of 400s. (Limits shipping from warehouse.)
# - Warehouse space is unlimited!
# - Factory has job limit of 2s. (Up to 18) (Limits creation of new jobs.)

# name rolls complexity accessory
species_data = '''
Shoyru     1 2 a
Grundo     1 2 n
Aisha      2 3 a
Chomby     2 3 a
Eyrie      2 4 a
Krawk      2 7 a
Kyrii      2 4 a
Peophin    2 5 a
Pteri      2 6 a
Skeith     2 6 a
Uni        2 7 a
Usul       2 5 a
Wocky      2 3 a
Blumaroo   2 2 n
Flotsam    2 4 n
Gelert     2 5 n
Jubjub     2 5 n
Mynci      2 6 n
Nimmo      2 3 n
Bori       3 6 a
Bruce      3 4 a
Buzz       3 9 a
Chia       3 3 a
Cybunny    3 5 a
Gnorbu     3 6 a
Grarrl     3 5 a
Hissi      3 7 a
Ixi        3 6 a
Kau        3 7 a
Kiko       3 5 a
Koi        3 5 a
Moehog     3 6 a
Tonu       3 6 a
Tuskaninny 3 5 a
Acara      3 5 n
Jetsam     3 4 n
Kacheek    3 3 n
Lenny      3 5 n
Lupe       3 5 n
Meerca     3 4 n
Poogle     3 3 n
Quiggle    3 3 n
Scorchio   3 4 n
Techo      3 4 n
Draik      4 9 a
Elephante  4 8 a
Kougra     4 5 a
Lutari     4 8 a
Xweetok    4 7 a
Yurble     4 5 a
Zafara     4 7 a
Korbat     4 5 n
Ruki       5 10 a
Ogrin      6 10 a
'''.strip().splitlines()
species_data = [tuple(l.split()) for l in species_data]
cloths = dict((s[0], int(s[1])) for s in species_data)
complexity = dict((s[0], int(s[2])) for s in species_data)
accessorized = dict((s[0], s[3] == 'a') for s in species_data)
all_species = [s[0] for s in species_data]

def mkpath(suffix):
    return f'/games/tycoon/{suffix}'

def amt(x):
    return int(x.split()[0].replace(',', ''))

path = mkpath('index.phtml')
path_factory = mkpath('factory.phtml')
path_store = mkpath('store.phtml')
path_materials = mkpath('materials.phtml')
path_workers_hire = mkpath('workers_hire.phtml')
path_process_hire = mkpath('process_hire.phtml')
path_warehouse = mkpath('warehouse.phtml')

def table_to_tuples(tbl, raw=False):
    result = []
    trs = re.findall(r'<tr.*?>(.*?)</tr>', tbl, flags=re.DOTALL)
    for i,tr in enumerate(trs):
        tds = re.findall(r'<td.*?>(.*?)</td>', tr, flags=re.DOTALL)
        tds = tuple(tds) if raw else tuple(map(lib.strip_tags, tds))
        result.append(tds)
    return result

# Plays Plushie Tycoon.
# Currently just does housecleaning, but the goal is that it eventually plays
# the whole thing (statelessly, of course).
def plushie_tycoon():
    np = lib.NeoPage(path)
    cash = amt(np.search(r'Cash on Hand: (.*?) NP')[1])
    print(f'Cash on Hand: {cash}')

    latest_price_by_species = {}
    plushies_to_sell = None
    jobs_to_sell = None

    if True:
        print('Plushie Tycoon: Checking on store.')
        np.get(path_store)
        np.get(path_store, 'Cat=0', 'invent=2')
        tbl = np.search(r"<table width='75%'.*?>(.*?)</table>")
        inv = []
        past_sales = []
        if tbl:
            tbl = tbl[1]
            inv = table_to_tuples(tbl)[1:]
            plushies_to_sell = sum(int(x[4]) for x in inv)
            jobs_to_sell = len(inv)
        else:
            plushies_to_sell = 0
            jobs_to_sell = 0
        print(f'Plushie Tycoon: Store has {plushies_to_sell} plushies over {jobs_to_sell} jobs left to sell.')
        np.get(path_store, 'Cat=0', 'invent=1')
        tbl = np.search(r"<table width='75%'.*?>(.*?)</table>")
        if tbl:
            tbl = tbl[1]
            past_sales = table_to_tuples(tbl)[1:]
        # TODO: Is inv in the correct order?
        for x in past_sales + inv:
            species = x[0]
            price = int(x[2])
            latest_price_by_species[species] = price
        print(f'Plushie Tycoon: Latest prices: {latest_price_by_species}')
        np.get(path_store, 'Cat=2')
        size = int(np.search(r'You now have a size (\d+) store')[1])
        print(f'Plushie Tycoon: Store is size {size}')

    if True:
        print('Plushie Tycoon: Checking on warehouse.')
        np.get(path_warehouse)
        tbl = np.search(r"<table border='0' width='90%'.*?>(.*?)</table>")[1]
        to_ship = table_to_tuples(tbl, raw=True)[2:-2]
        args = []
        for row in to_ship:
            status = row[4]
            if status == 'Loaded':
                chkbox = row[5]
                result = re.search(r"name='(.*?)' value='(.*?)'", chkbox)
                name = result[1]
                value = result[2]
                args.append(f'{name}={value}')
        if args:
            print(f'Shipping {len(args)} orders to the warehouse.')
            args.append('submit=Ship Plushies')
            np.post(path_warehouse, *args)

    num_factory_jobs = None
    if True:
        # Check status of jobs.
        # If less than 500 plushies remain, fire all workers.
        # Else, hire up to 250 Trainees and 25 Managers.
        print('Plushie Tycoon: Checking on factory.')
        np.get(path_factory, 'exist=1')
        tbl = np.search(r"<table border='0' width='70%'.*?>(.*?)</table>")[1]
        jobs = table_to_tuples(tbl)[1:-1]
        num_factory_jobs = len(jobs)
        num_plushies = sum(int(total) - int(done) for pet, total, done in jobs)
        print(f'Plushie Tycoon: Factory has {num_plushies} plushies in {num_factory_jobs} jobs.')
        if num_plushies < 300 or num_factory_jobs >= 5:
            np.get(path_factory, 'personnel=1')
            if np.contains('factory.phtml?personnel=2&fire=1'):
                np.get(path_factory, 'personnel=2', 'fire=1')
                if np.contains('fire_all=1'):
                    np.get(path_factory, 'fire_all=1')
                    print('Plushie Tycoon: Fired all workers.')
            else:
                print('Plushie Tycoon: Already fired all workers.')
        else:
            np.get(path_factory, 'personnel=1')
            if np.contains('many unemployed pets'):
                # Use the default workforce
                np.get(path_factory, 'set_def=2', 'personnel=1')
                print('Plushie Tycoon: Hired the default workforce.')
                #np.get(path_factory, 'personnel=2', 'hire=1')
                #np.get(path_workers_hire, 'worker=2')
                #np.post(path_process_hire, 'amt=250', 'worker=2')
                #np.get(path_workers_hire, 'worker=4')
                #np.post(path_process_hire, 'amt=10', 'worker=4')
                #np.get(path_workers_hire, 'worker=4')
                #np.post(path_process_hire, 'amt=10', 'worker=4')
                #np.get(path_workers_hire, 'worker=4')
                #np.post(path_process_hire, 'amt=4', 'worker=4')
                #print('Plushie Tycoon: Hired up to 250 Trainees and 25 Managers.')
            else:
                print('Plushie Tycoon: Already have workers.')

    rois = []
    if True:
        print('Plushie Tycoon: Checking on materials.')
        np.get(path_materials)
        np.get(path_materials, 'Cat=0')
        tbl = np.search(r"<table width='80%'.*?>(.*?)</table>")[1]
        inv = table_to_tuples(tbl)
        green_price = amt(inv[-1][3])

        np.get(path_materials, 'Cat=1')
        tbl = np.search(r"<table width='80%'.*?>(.*?)</table>")[1]
        inv = table_to_tuples(tbl)
        cotton_price = amt(inv[-1][0])

        np.get(path_materials, 'Cat=2')
        tbl = np.search(r"<table width='80%'.*?>(.*?)</table>")[1]
        inv = table_to_tuples(tbl)
        gem_price = amt(inv[-1][0])

        np.get(path_materials, 'Cat=3')
        tbl = np.search(r"<table width='80%'.*?>(.*?)</table>")[1]
        inv = table_to_tuples(tbl)
        bag_price = amt(inv[-1][0])

        for s in all_species:
            if cloths[s] < 4: continue
            if not accessorized[s]: continue
            cost = cloths[s] * green_price
            cost += cotton_price
            cost += bag_price
            if accessorized[s]: cost += gem_price
            total_cost = cost + 1000 + 278
            last_price = latest_price_by_species.get(s)
            if last_price:
                revenue = 100 * last_price
                profit = revenue - total_cost
                roi = profit / total_cost
                rois.append((s, roi))
                print(f'100x{s: <12}: ROI {roi:.3f}; cost {total_cost}; last revenue {last_price * 100}; cloths {cloths[s]}')
            else:
                print(f'100x{s: <12}: ROI ?????. cost {total_cost}; cloths {cloths[s]}')

    # Determine which kinds of plushies should be built, based on free space in
    # the pipeline and profitability of each species.
    # TODO: Also consider other materials used in plushies.
    if True:
        rois.sort(key=lambda x:x[1], reverse=True)

if __name__ == '__main__':
    plushie_tycoon()
