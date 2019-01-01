from collections import defaultdict
import re
import subprocess
from datetime import datetime
import time
import os

from lib import NeoPage

path_index = '/medieval/shapeshifter_index.phtml'
path_game = '/medieval/shapeshifter.phtml'
path_process = '/medieval/process_shapeshifter.phtml'

def make_kvho_input(goal_grid, shape_grids, goal_idx):
    parts = []
    R = len(goal_grid)
    C = len(goal_grid[0])

    parts.append(f'{C} {R}')
    for row in goal_grid:
        parts.append(' '.join(map(str, row)))
    parts.append(f'{goal_idx}')
    parts.append(f'{len(shape_grids)}')
    for grid in shape_grids:
        parts.append(str(sum(map(sum, grid))) + ' ' + ' '.join(
            str(r * C + c)
            for r, row in enumerate(grid)
            for c, x in enumerate(row)
            if x))

    return '\n'.join(parts)

def shapeshifter(timeout=10*60):
    np = NeoPage()
    np.get(path_index)
    starting_np = np.current_np()
    if np.contains('Continue Game!'):
        np.get(path_game)
    elif np.contains('Start Game!'):
        np.post(path_process, f'type=init')

    # Just in case we won but left it in the completed state
    if np.contains('You Won!') or np.contains('You Lost!'):
        np.post(path_process + '?type=init')

    tbl = np.search(r'''<table border=1 bordercolor='gray'>(.*?)</table>''')[1]
    imgs = re.findall(r'''<img src='(.*?)' border=0 name='i_'>(<br><b><small>GOAL</small></b></td>)?''', tbl)
    imgs = imgs[:-1]
    N = len(imgs)
    goal_idx = next(i for i, (_, goal) in enumerate(imgs) if goal)
    to_idx = {img: i for i, (img, _) in enumerate(imgs)}

    tbl = np.search(r'''<table align=center cellpadding=0 cellspacing=0 border=0>(.*?)</table>''')[1]
    goal_grid = []
    for row in re.findall(r'''<tr>(.*?)</tr>''', tbl, flags=re.DOTALL):
        imgs = re.findall(r'''<img src='(.*?)' .*?>''', row)
        goal_row = [to_idx[img] for img in imgs]
        goal_grid.append(goal_row)

    tbl = np.search(r'''<center><b><big>ACTIVE SHAPE</big></b><p>(.*?)</table>\n''')[1]
    shape_grids = []
    for shape_info in re.findall(r'''<table.*?>(.*?)</table>''', tbl):
        grid = []
        for row_info in re.findall(r'''<tr>(.*?)</tr>''', shape_info):
            tiles = re.findall(r'''<td.*?>(.*?)</td>''', row_info)
            grid.append([int('square.gif' in tile_info) for tile_info in tiles])
        shape_grids.append(grid)

    # Compute kvho difficulty.
    R = len(goal_grid)
    C = len(goal_grid[0])
    min_shifts_needed = R * C * (N - 1) - sum(map(sum, goal_grid))
    shifts_available = sum(sum(sum(rows) for rows in grid) for grid in shape_grids)
    num_overshifts = shifts_available - min_shifts_needed
    num_flips = num_overshifts // N
    print(f'Puzzle permits {num_flips} flips ({num_overshifts} overshifts)')

    kvho_input = make_kvho_input(goal_grid, shape_grids, goal_idx)

    print(f'Waiting for kvho.')
    start_time = datetime.now()

    positions = []
    try:
        proc = subprocess.run(['c/ss'], input=kvho_input, encoding='utf-8', capture_output=True, timeout=timeout)
        for line in proc.stdout.splitlines():
            if 'x' in line and '=' in line:
                x = list(map(int, line.replace('x', ' ').replace('=', ' ').strip().split()))
                for c, r, _ in zip(x[::3], x[1::3], x[2::3]):
                    positions.append((r, c))
        print(f'Solution found in {datetime.now() - start_time}: {positions}')
    except subprocess.TimeoutExpired:
        print(f'Solution not found in time. Throwing this puzzle to get a new one.')
        for _ in shape_grids:
            positions.append((0, 0))

    for i, (shape, (r, c)) in enumerate(zip(shape_grids, positions)):
        print(f'\rPlacing piece {i+1}/{len(positions)}', end='')
        np.set_referer_path(path_game)
        np.get(path_process, 'type=action', f'posx={c}', f'posy={r}')
        time.sleep(0.5)
    print()

    if np.contains('You Won!'):
        np.set_referer_path(path_game)
        np.post(path_process + '?type=init')
        ending_np = np.current_np()
        print(f'Done level, earned {ending_np - starting_np} NP')
        return 1
    elif np.contains('reached your max neopoints'):
        print('Done for today.')
        return 2
    else:
        print('Did not solve level??')
        return 0

def shapeshifter_all():
    while True:
        if shapeshifter() == 2:
            break

def shapeshifter_one():
    timeout = 10
    while True:
        print(f'Timeout {timeout} sec.')
        result = shapeshifter(timeout)
        if result == 0:
            timeout = round(timeout * 1.5)
        else:
            break

def goto_level(lvl):
    np = NeoPage()
    #np.set_referer_path(path_game)
    #np.post(path_process, 'type=reset_this_thing', 'username={os.environ["NP_USER"]}')
    #print(np.last_file_path)

    #if shapeshifter(timeout=0) == 2:
    #    print('Shapeshifter: Already done.')
    #    return

    np.set_referer_path(path_game)
    np.post(path_process + '?type=init', f'past_level={lvl}')
    print(np.last_file_path)

def shapeshifter_daily():
    goto_level(94)
    while shapeshifter(timeout=5) != 2:
        pass

if __name__ == '__main__':
    #shapeshifter_one()
    goto_level(94)
