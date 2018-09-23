#!/usr/bin/env python3
from collections import defaultdict, Counter
import bisect
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
path_materials_buy = mkpath('materials_buy.phtml')
path_process_purchase = mkpath('process_purchase.phtml')
path_workers_hire = mkpath('workers_hire.phtml')
path_process_hire = mkpath('process_hire.phtml')
path_warehouse = mkpath('warehouse.phtml')

def check_store(np):
    #print('Plushie Tycoon: Checking on store.')
    species_stats = {}
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
    prices = defaultdict(list)
    for row in past_sales + inv:
        species = row[0]
        price = int(row[2])
        prices[species].append(price)
    for species in prices.keys():
        ps = prices[species]
        n = len(ps)
        last = ps[-1]
        avg = sum(ps) / n
        stdev = (sum((p - avg)**2 for p in ps) / n)**0.5
        species_stats[species] = {
            'last': last,
            'min': min(ps),
            'max': max(ps),
            'avg': avg,
            'median': ps[len(ps) // 2],
            'stdev': stdev,
        }
    #np.get(path_store, 'Cat=2')
    #size = int(np.search(r'You now have a size (\d+) store')[1])
    return species_stats

def check_warehouse(np):
    #print('Plushie Tycoon: Checking on warehouse.')
    np.get(path_warehouse)
    tbl = np.search(r"<table border='0' width='90%'.*?>(.*?)</table>")[1]
    to_ship = lib.table_to_tuples(tbl, raw=True)[2:-2]
    if to_ship:
        print(f'Plushie Tycoon: Warehouse is loading {len(to_ship)} jobs.')
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
        # TODO: Only ship items to the store if it is advantageous.
        # (tax situations?)
        print(f'Plushie Tycoon: Shipping {len(args)} jobs to the store.')
        args.append('submit=Ship Plushies')
        np.post(path_warehouse, *args)

def check_factory(np, hire=False):
    # Check status of jobs.
    # If less than 500 plushies remain, fire all workers.
    # Else, hire up to 250 Trainees and 25 Managers.
    #print('Plushie Tycoon: Checking on factory.')
    np.get(path_factory, 'exist=1')
    tbl = np.search(r"<table border='0' width='70%'.*?>(.*?)</table>")[1]
    jobs = lib.table_to_tuples(tbl)[1:-1]
    num_factory_jobs = len(jobs)
    num_plushies = sum(int(total) - int(done) for pet, total, done in jobs)
    print(f'Plushie Tycoon: Factory has {num_plushies} plushies in {num_factory_jobs} jobs.')
    if hire:
        if num_plushies > 400 or num_factory_jobs >= 5:
            np.get(path_factory, 'personnel=1')
            if np.contains('many unemployed pets'):
                # Use the default workforce
                np.get(path_factory, 'set_def=2', 'personnel=1')
                print('Plushie Tycoon: Hired the default workforce.')
                # TODO: Calculate a good workforce and hire it.
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
    return num_factory_jobs

def check_materials(np):
    #print('Plushie Tycoon: Checking on materials.')
    np.get(path_materials)
    material_prices = []
    material_owned = []
    buy_links = []
    accessories_owned = defaultdict(int)
    for cat in range(0, 4):
        np.get(path_materials, f'Cat={cat}')
        tbl = np.search(r"<table width='80%'.*?>(.*?)</table>")[1]
        rows = lib.table_to_tuples(tbl, raw=True)

        material_prices.append([amt(x) for x in rows[-1]])
        if len(rows[-3]) > 1:
            material_owned.append([amt(x) for x in rows[-3]])
        else:
            material_owned.append([0, 0, 0, 0])

        links = []
        for link_text in rows[1]:
            links.append(re.search(r"onClick=buying\('(.*?)',", link_text)[1])
        buy_links.append(links)

        if cat == 2 and np.contains("table  width='80%'"):
            tbl2 = np.search(r"<table  width='80%' .*?>(.*?)</table>")[1]
            rows = lib.table_to_tuples(tbl2)[2:]
            for s, quant, kind, _ in rows:
                if quant:
                    accessories_owned[s] += amt(quant)
    return material_prices, material_owned, accessories_owned, buy_links

def calculate_rois(material_prices, species_stats):
    rois = []
    green_price = material_prices[0][3]
    cotton_price = material_prices[1][0]
    gem_price = material_prices[2][0]
    bag_price = material_prices[3][0]

    for s in all_species:
        if cloths[s] < 3: continue
        if not accessorized[s]: continue
        cost = cloths[s] * green_price
        cost += cotton_price
        cost += bag_price
        if accessorized[s]: cost += gem_price
        total_cost = cost + 500 + 278
        stats = species_stats.get(s)
        if stats:
            last_price = stats['last']
            revenue = 100 * last_price
            profit = revenue - total_cost
            roi = profit / total_cost
            rois.append((s, total_cost, roi))
        else:
            rois.append((s, total_cost, None))

    rois.sort(key=lambda x:x[-1] or -9999.9, reverse=True)
    return rois

def pick_plushies(cash, rois, accessories_owned, num_jobs):
    jobs = []
    np_left = cash - 30000
    # Pick a random species, weighing high-ROI species higher. Unknown
    # ROIs are treated as if they had an ROI of +100%.
    weights = [20.0**max(0.0, roi or 1.0) for _, _, roi in rois]
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]
    cumul_weights = [weights[0]]
    for w in weights[1:]:
        cumul_weights.append(w + cumul_weights[-1])

    # Create jobs that will use existing accessories
    max_cost = max(total_cost for _, total_cost, _ in rois)
    rec_job_size = max(1, min(2, np_left // max_cost // 2))

    for s, n in accessories_owned.items():
        for i in range(0, n, rec_job_size):
            job_size = min(rec_job_size, n - i)
            jobs.append((s, job_size))
            np_left -= 5000 * job_size
            if len(jobs) >= num_jobs: break
        if len(jobs) >= num_jobs: break

    while np_left > 0 and len(jobs) < num_jobs:
        s, total_cost, roi = random.choice(rois)
        r = random.random()
        i = bisect.bisect_left(cumul_weights, r)
        s, total_cost, roi = rois[i]
        np_left -= total_cost * rec_job_size
        if np_left > 0 and len(jobs) < num_jobs:
            jobs.append((s, rec_job_size))

    return jobs

def buy_materials_up_to(np, amounts, buy_links,
        material_prices, material_owned, accessories_owned,
        accessory_species):
    species_iter = iter(accessory_species.items())
    if sum(amounts) >= 100:
        print('Warning: Want to buy TOO MUCH!')
        return
    for cat, amt in enumerate(amounts):
        item = 3 if cat == 0 else 0
        np.get(path_materials, f'Cat={cat}')
        while material_owned[cat][item] < amounts[cat]:
            amt_to_buy = min(amounts[cat] - material_owned[cat][item], 10)
            total_cost = material_prices[cat][item] * amt_to_buy
            np.set_referer_path(f'{path_materials}?Cat={cat}')
            np.get(f'/games/tycoon/{buy_links[cat][item]}')
            product = np.search(r"<input type='hidden' name='product' value='(.*?)'>")[1]
            purchaser = np.search(r"<input type='submit' name='purchaser' value='(.*?)'>")[1]
            args = []
            if cat == 2:
                s, quant = next(species_iter)
                s_num = np.search(f"<option value='(\d+)'>{s}</option>")[1]
                amt_to_buy = min(amt_to_buy, quant - accessories_owned[s])
                args.append(f'amt={amt_to_buy}')
                args.append(f'pickpet={s_num}')
                print(f'Plushie Tycoon: Buying {amt_to_buy}x ({cat}, {item}, {s})')
            else:
                print(f'Plushie Tycoon: Buying {amt_to_buy}x ({cat}, {item})')
                args.append(f'amt={amt_to_buy}')
            args.append(f'total_amt={total_cost} NP')
            args.append(f'product={product}')
            args.append(f'purchaser={purchaser}')
            np.post(path_process_purchase, *args)
            material_owned[cat][item] += amt_to_buy

def start_jobs(np, jobs):
    for s, qty in jobs:
        np.get(path_factory, 'start=1')
        np.post(path_factory, f'pickpet={s}')
        if np.contains('increase the size of your factory'):
            link = np.search(r'<b>Click</b> <a href="(.*?)"><b>here</b></a> <b>to pay')[1]
            np.get(link)
            np.get(path_factory, 'start=1')
            np.post(path_factory, f'pickpet={s}')
        args = []
        cloth = np.search(r"<input type='radio' name='Cloth' value='(.*?)'>")[1]
        stuffing = np.search(r"<input type='radio' name='Stuffing' value='(.*?)'>")[1]
        accessories = np.search(r"<input type='radio' name='Accessories' value='(.*?)'>")
        packing = np.search(r"<input type='radio' name='Packing' value='(.*?)'>")[1]
        species = np.search(r"<input type='hidden' name='species' value='(.*?)'>")[1]
        submit_job = np.search(r"<input type='submit' name='submitjob' value='(.*?)'>")[1]
        args.append(f'Cloth={cloth}')
        args.append(f'Stuffing={stuffing}')
        if accessories: args.append(f'Accessories={accessories[1]}')
        args.append(f'Packing={packing}')
        args.append(f'species={species}')
        args.append(f'submitjob={submit_job}')
        np.post(path_factory, *args)
        args = []
        args.append(f'qnt_to_make={qty}')
        for name, value in np.findall(r"<input type='hidden' name='(.*?)' value='(.*?)'>"):
            args.append(f'{name}={value}')
        print(f'Plushie Tycoon: Starting job for {qty}00x{s}')
        np.post(path_factory, *args)

# Plays Plushie Tycoon.
# Currently just does housecleaning, but the goal is that it eventually plays
# the whole thing (statelessly, of course).
def plushie_tycoon(details=False):
    np = lib.NeoPage(path)
    cash = amt(np.search(r'Cash on Hand: (.*?) NP')[1])
    print(f'Cash on Hand: {cash}')

    species_stats = check_store(np)
    check_warehouse(np)
    num_factory_jobs = check_factory(np, hire=True)
    material_prices, material_owned, accessories_owned, buy_links = check_materials(np)
    rois = calculate_rois(material_prices, species_stats)

    # Determine which kinds of plushies should be built, based on free space in
    # the factory and profitability of each species.
    # TODO: Also consider other materials used in plushies.
    if details:
        print(f'{"Species (cloths)": <21} {"roi": <6} {"cost": <5} {"lst": <3} {"range": <7} {"avg": <6} {"med": <3} {"stdev": <6}')
        for s, total_cost, roi in rois:
            stats = species_stats.get(s)
            roi_ = f'{roi:+.3f}' if roi else '??????'
            print(f'100x{s: <12} ({cloths[s]}): {roi_} {total_cost: >5} {stats["last"]: >3} {stats["min"]: >3}-{stats["max"]: >3} {stats["avg"]: >6.2f} {stats["median"]: >3} {stats["stdev"]: >6.3f}')

    num_jobs = 18 - num_factory_jobs
    jobs = pick_plushies(cash, rois, accessories_owned, num_jobs)
    jobs_chunked = []
    cur_chunk = []
    total_inv_slots = 0
    for s, qty in jobs:
        inv_slots = qty * (cloths[s] + 3)
        if inv_slots + total_inv_slots > 100:
            jobs_chunked.append(cur_chunk)
            cur_chunk = []
            total_inv_slots = 0
        cur_chunk.append((s, qty))
        total_inv_slots += inv_slots
    if cur_chunk: jobs_chunked.append(cur_chunk)
    print(f'Chunks: {jobs_chunked}')
    for job_chunk in jobs_chunked:
        print(f'Building job chunk {job_chunk}')
        accessory_species = defaultdict(int)
        for s, qty in job_chunk:
            accessory_species[s] += qty
        n_cloths = sum(qty * cloths[s] for s, qty in job_chunk)
        n_other = sum(qty for s, qty in job_chunk)
        print(f'Goods needed: {n_cloths} cloth, {n_other} other.')
        # TODO: Do something better than re-checking this.
        material_prices, material_owned, accessories_owned, buy_links = check_materials(np)
        buy_materials_up_to(np, [n_cloths, n_other, n_other, n_other],
            buy_links, material_prices, material_owned,
            accessories_owned, accessory_species)
        start_jobs(np, job_chunk)
    check_factory(np, hire=True)

if __name__ == '__main__':
    plushie_tycoon(True)
