#!/usr/bin/env python3
import random
import re

import lib
from lib import amt

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

path = mkpath('index.phtml')
path_factory = mkpath('factory.phtml')
path_store = mkpath('store.phtml')
path_materials = mkpath('materials.phtml')
path_workers_hire = mkpath('workers_hire.phtml')
path_process_hire = mkpath('process_hire.phtml')
path_warehouse = mkpath('warehouse.phtml')

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
            inv = lib.table_to_tuples(tbl)[1:]
            plushies_to_sell = sum(int(x[1]) - int(x[4]) for x in inv)
            jobs_to_sell = len(inv)
        else:
            plushies_to_sell = 0
            jobs_to_sell = 0
        print(f'Plushie Tycoon: Store has {plushies_to_sell} plushies over {jobs_to_sell} jobs left to sell.')
        np.get(path_store, 'Cat=0', 'invent=1')
        tbl = np.search(r"<table width='75%'.*?>(.*?)</table>")
        if tbl:
            tbl = tbl[1]
            past_sales = lib.table_to_tuples(tbl)[1:]
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
        to_ship = lib.table_to_tuples(tbl, raw=True)[2:-2]
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
        jobs = lib.table_to_tuples(tbl)[1:-1]
        num_factory_jobs = len(jobs)
        num_plushies = sum(int(total) - int(done) for pet, total, done in jobs)
        print(f'Plushie Tycoon: Factory has {num_plushies} plushies in {num_factory_jobs} jobs.')
        if num_plushies > 400 or num_factory_jobs >= 5:
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
        else:
            np.get(path_factory, 'personnel=1')
            if np.contains('factory.phtml?personnel=2&fire=1'):
                np.get(path_factory, 'personnel=2', 'fire=1')
                if np.contains('fire_all=1'):
                    np.get(path_factory, 'fire_all=1')
                    print('Plushie Tycoon: Fired all workers.')
            else:
                print('Plushie Tycoon: Already fired all workers.')

    rois = []
    if True:
        print('Plushie Tycoon: Checking on materials.')
        np.get(path_materials)
        np.get(path_materials, 'Cat=0')
        tbl = np.search(r"<table width='80%'.*?>(.*?)</table>")[1]
        inv = lib.table_to_tuples(tbl)
        green_price = amt(inv[-1][3])

        np.get(path_materials, 'Cat=1')
        tbl = np.search(r"<table width='80%'.*?>(.*?)</table>")[1]
        inv = lib.table_to_tuples(tbl)
        cotton_price = amt(inv[-1][0])

        np.get(path_materials, 'Cat=2')
        tbl = np.search(r"<table width='80%'.*?>(.*?)</table>")[1]
        inv = lib.table_to_tuples(tbl)
        gem_price = amt(inv[-1][0])

        np.get(path_materials, 'Cat=3')
        tbl = np.search(r"<table width='80%'.*?>(.*?)</table>")[1]
        inv = lib.table_to_tuples(tbl)
        bag_price = amt(inv[-1][0])

        for s in all_species:
            if cloths[s] < 3: continue
            if not accessorized[s]: continue
            cost = cloths[s] * green_price
            cost += cotton_price
            cost += bag_price
            if accessorized[s]: cost += gem_price
            total_cost = cost + 500 + 278
            last_price = latest_price_by_species.get(s)
            if last_price:
                revenue = 100 * last_price
                profit = revenue - total_cost
                roi = profit / total_cost
                rois.append((s, total_cost, roi))
            else:
                rois.append((s, total_cost, None))

    # Determine which kinds of plushies should be built, based on free space in
    # the pipeline and profitability of each species.
    # TODO: Also consider other materials used in plushies.
    if True:
        rois.sort(key=lambda x:x[-1] or -9999.9, reverse=True)
        for s, total_cost, roi in rois:
            last_price = latest_price_by_species.get(s)
            roi_ = f'{roi:+.3f}' if roi else '??????'
            print(f'100x{s: <12} ({cloths[s]}): ROI {roi_}; cost {total_cost}; last rev {last_price}')
        jobs = []
        num_jobs_to_make = 18 - num_factory_jobs
        np_left = cash - 14000
        while np_left > 0 and num_jobs_to_make > 0:
            s, total_cost, roi = random.choice(rois)
            if random.random() < 0.5:
                # Exploit. Pick a random species whose ROI is at least 66% of
                # the best one, weighted heavily towards higher ROIs.
                k = 0
                for _, _, roi in rois:
                    if roi and roi > rois[0][2] * 0.7: k += 1
                    if random.random() < 0.5: break
                if k > 0:
                    s, total_cost, roi = rois[random.randint(0, k-1)]
            else:
                # Explore. Pick a random species, weighing high-ROI species
                # slightly higher. Unknown ROIs are treated as if they had an
                # ROI of +100%.
                weights = [2.0**(roi or 1.0) for _, _, roi in rois]
                total_weight = sum(weights)
                weights = [w / total_weight for w in weights]
                cumul_weights = [weights[0]]
                for w in weights[1:]:
                    cumul_weights.append(w + cumul_weights[-1])
                r = random.random()
                # This is O(n) and could be O(log n) but I can't be bothered.
                for i, w in enumerate(cumul_weights):
                    if w < r:
                        s, total_cost, roi = rois[i]
                        break
            np_left -= total_cost
            num_jobs_to_make -= 1
            if np_left > 0 and num_jobs_to_make > 0:
                jobs.append(s)

        print(f'Recommended jobs: 100x{jobs}')
        n_cloths = sum(cloths[s] for s in jobs)
        n_other = len(jobs)
        print(f'Goods needed: {n_cloths} cloth, {n_other} other.')

if __name__ == '__main__':
    plushie_tycoon()
