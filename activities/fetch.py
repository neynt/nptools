from collections import defaultdict
import heapq
import re
import time
import random

from lib import NeoPage
from lib import util

C_GREY = '\033[37m'
C_RED = '\033[1;91m'
C_GREEN = '\033[1;92m'
C_YELLOW = '\033[1;93m'
C_CYAN = '\033[1;96m'
C_ENDC = '\033[0m'

UP = 1
LEFT = 2
DOWN = 4
RIGHT = 8

DIRS = [UP, LEFT, DOWN, RIGHT]

dir_to_delta = {
    UP: (0, -1),
    LEFT: (-1, 0),
    DOWN: (0, 1),
    RIGHT: (1, 0),
}

opp_dir = {
    UP: DOWN,
    LEFT: RIGHT,
    RIGHT: LEFT,
    DOWN: UP,
}

DELTAS = dir_to_delta.values()

maze_sizes = {
    '1': 10,
    '2': 15,
    '3': 20,
    '4': 25,
    '5': 30,
}

img_to_dirs = {
    'path_iso': 0,
    'path_u': UP,
    'path_d': DOWN,
    'path_l': LEFT,
    'path_r': RIGHT,
    'path_lu': UP | LEFT,
    'path_ud': UP | DOWN,
    'path_ru': UP | RIGHT,
    'path_ld': LEFT | DOWN,
    'path_lr': LEFT | RIGHT,
    'path_rd': DOWN | RIGHT,
    'path_t_u': UP | LEFT | RIGHT,
    'path_t_l': LEFT | UP | DOWN,
    'path_t_d': DOWN | LEFT | RIGHT,
    'path_t_r': RIGHT | UP | DOWN,
    'path_x': UP | LEFT | DOWN | RIGHT,
}

dirs_to_unicode = {
    -1: '?',
    0: ' ',
    UP: '╵',
    LEFT: '╴',
    RIGHT: '╶',
    DOWN: '╷',
    UP | LEFT: '┘',
    UP | DOWN: '│',
    UP | RIGHT: '└',
    LEFT | DOWN: '┐',
    LEFT | RIGHT: '─',
    DOWN | RIGHT: '┌',
    UP | LEFT | DOWN: '┤',
    UP | DOWN | RIGHT: '├',
    UP | LEFT | RIGHT: '┴',
    LEFT | DOWN | RIGHT: '┬',
    UP | LEFT | DOWN | RIGHT: '┼',
}

UNKNOWN_COST = 3

path = '/games/maze/maze.phtml'

def xs(l): return [x for x, y in l]
def ys(l): return [y for x, y in l]

def fetch(verbose=False):
    log = open('fetch.log', 'a')
    np = NeoPage()
    # TODO: Figure out how to continue on from existing game.
    np.get(path, 'deletegame=1')

    # Start new game.
    diffs = re.findall(r'<A HREF="maze.phtml\?create=1&diff=(\d+)">', np.content)
    diff = '5' if '5' in diffs else '3'
    np.get(path, 'create=1', f'diff={diff}')
    maze_size = maze_sizes[diff]

    goal_item_img, goal_item = re.search(r'<IMG SRC="http://images.neopets.com/games/maze/(item_.*?)" WIDTH="80" HEIGHT="80"><br><b>(.*?)</b>', np.content).group(1, 2)
    print(f'Asked to find {goal_item} (img: {goal_item_img})')
    np.post(path)

    # State for a single game.
    maze = {}
    x_start = 0
    y_start = 0
    x_cur = x_start
    y_cur = y_start
    x_lower = -maze_size + 1
    x_upper = maze_size - 1
    y_lower = -maze_size + 1
    y_upper = maze_size - 1
    xy_item = None
    xy_exit = None

    while True:
        # Check end conditions.
        if np.contains('Success! You fetched the item and reached the exit!'):
            prize = util.amt(re.search(r'You have been awarded <b>(.*?)</b> for your efforts!', np.content)[1])
            print(f'Won! Got {prize} NP')
            if np.contains('You have achieved a streak'):
                streak, cumul = re.search(r'You have achieved a streak of <b>(.*?)</b> victories, for a running total of <b>(.*?)</b> points', np.content).group(1, 2)
                print(f'Streak is {streak}, total score {cumul}')
            else:
                streak = 1
                cumul = prize
            log.write(f'{diff},{UNKNOWN_COST},1,{prize},{streak},{cumul}\n')
            return (prize, streak, cumul)
        elif np.contains("Your master is very displeased!"):
            print(f'Ran out of time! :(')
            log.write(f'{diff},{UNKNOWN_COST},0,0,0,0\n')
            return

        moves_remaining = int(re.search(r'Moves Remaining: <b>(.*?)</b>', np.content)[1].split()[0])

        # Update knowledge.
        tbl = re.search(r'<TABLE BORDER="0" CELLPADDING="0" CELLSPACING="0" WIDTH="400">(.*?)</TABLE>', np.content, flags=re.DOTALL)[1]
        tiles = re.findall(r'<TD BACKGROUND="http://images.neopets.com/games/maze/(.*?).gif" WIDTH="80" HEIGHT="80".*?>(.*?)</TD>', tbl)

        for jitter_x, jitter_y in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            tiles_iter = iter(tiles)
            good = True
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    img, content = next(tiles_iter)
                    x = x_cur + jitter_x + dx
                    y = y_cur + jitter_y + dy
                    if (x, y) in maze and maze[x, y] != img_to_dirs[img]:
                        good = False
            if good:
                x_cur += jitter_x
                y_cur += jitter_y
                break

        tiles_iter = iter(tiles)
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                img, content = next(tiles_iter)
                x = x_cur + dx
                y = y_cur + dy

                dirs = img_to_dirs[img]
                maze[x, y] = dirs

                if 'http://images.neopets.com/games/maze/item_' in content:
                    xy_item = (x, y)

                # Update knowledge of bounds
                if dirs == 0:
                    if dx == 0:
                        if dy < 0:
                            y_lower = max(y_lower, y_cur + dy + 1)
                            y_upper = y_lower + maze_size - 1
                        elif dy > 0:
                            y_upper = min(y_upper, y_cur + dy - 1)
                            y_lower = y_upper - maze_size + 1
                    if dy == 0:
                        if dx < 0:
                            x_lower = max(x_lower, x_cur + dx + 1)
                            x_upper = x_lower + maze_size - 1
                        elif dx > 0:
                            x_upper = min(x_upper, x_cur + dx - 1)
                            x_lower = x_upper - maze_size + 1

                # Path leading out of bounds indicates an exit
                if x_lower <= x <= x_upper and y_lower <= y <= y_upper:
                    for d in DIRS:
                        ddx, ddy = dir_to_delta[d]
                        if dirs & d and not (x_lower <= x + ddx <= x_upper and y_lower <= y + ddy <= y_upper):
                            xy_exit = (x, y)

        # Compute the goals.
        got_item = not np.contains('Searching for:')
        goals = []
        if got_item:
            # Find the exit!!
            if xy_exit:
                goals = [xy_exit]
            else:
                # All points on any side opposite the side you started on.
                candidates = []
                if x_lower == 0: candidates.extend((x_upper, y) for y in range(y_lower, y_upper + 1))
                if x_upper == 0: candidates.extend((x_lower, y) for y in range(y_lower, y_upper + 1))
                if y_lower == 0: candidates.extend((x, y_upper) for x in range(x_lower, x_upper + 1))
                if y_upper == 0: candidates.extend((x, y_lower) for x in range(x_lower, x_upper + 1))
                # ... that has not been a confirmed dud
                goals = []
                for x, y in candidates:
                    good = False
                    for d in DIRS:
                        dx, dy = dir_to_delta[d]
                        if not (x_lower <= x + dx <= x_upper and y_lower <= y + dy <= y_upper) and (maze.get((x, y), -1) & d) and (maze.get((x + dx, y + dy), -1) & opp_dir[d]):
                            good = True
                            break
                    if good:
                        goals.append((x, y))
        else:
            if xy_item:
                goals = [xy_item]
            else:
                # Possibilities for item location.
                padding = maze_size // 2 - 1
                goals = [(x, y)
                        for x in range(x_lower + padding, x_upper - padding + 1)
                        for y in range(y_lower + padding, y_upper - padding + 1)
                        if (x, y) not in maze]

        # Dijkstra's to figure out how to best reach a goal.
        # Distance is (# ? tiles, # known steps).
        prevs = {}
        Q = [(0, (x_cur, y_cur), None)]
        reached_goal = None
        while Q:
            c, (x, y), prev = heapq.heappop(Q)
            if (x, y) in prevs: continue
            if (x, y) not in maze and not (x_lower <= x <= x_upper and y_lower <= y <= y_upper): continue
            prevs[x, y] = prev
            if (x, y) in goals:
                reached_goal = (x, y)
                break
            dirs = maze.get((x, y), -1)
            c_ = c + (UNKNOWN_COST if dirs == -1 else 1)
            for d in DIRS:
                dx, dy = dir_to_delta[d]
                dirs_ = maze.get((x + dx, y + dy), -1)
                if dirs & d and dirs_ & opp_dir[d]:
                    heapq.heappush(Q, (c_, (x + dx, y + dy), (x, y)))

        if not reached_goal:
            print(f'Ended up in a bad aimless state.')
            log.write(f'{diff},{UNKNOWN_COST},0,0,0,0,ERROR\n')
            return
        
        # Backtrace route to find which direction to walk in.
        cur = reached_goal
        route = []
        while cur:
            route.append(cur)
            cur = prevs[cur]
        route = route[::-1]

        x_nxt, y_nxt = route[1]
        dxdy = (x_nxt - x_cur, y_nxt - y_cur)
        movedir = None
        if dxdy == (-1, 0): movedir = 2
        elif dxdy == (1, 0): movedir = 3
        elif dxdy == (0, -1): movedir = 0
        elif dxdy == (0, 1): movedir = 1

        # Print the maze.
        movechar = "↑↓←→"[movedir]
        if verbose:
            coords = list(maze.keys()) + goals
            min_x = max(x_lower - 2, min(xs(coords)))
            max_x = min(x_upper + 2, max(xs(coords)))
            min_y = max(y_lower - 2, min(ys(coords)))
            max_y = min(y_upper + 2, max(ys(coords)))
            for y in range(min_y - 1, max_y + 2):
                for x in range(min_x - 1, max_x + 2):
                    c = dirs_to_unicode[maze.get((x, y), -1)]
                    if (x, y) == (x_cur, y_cur):
                        c = '@'
                    if (x, y) in goals:
                        c = C_YELLOW + c + C_ENDC
                    elif (x, y) in route:
                        c = (C_GREEN if got_item else C_RED) + c + C_ENDC
                    elif abs(x - x_cur) <= 2 and abs(y - y_cur) <= 2:
                        c = C_CYAN + c + C_ENDC
                    if c == '?':
                        c = C_GREY + c + C_ENDC
                    print(c, end='')
                print()
            print(f'Moves left: {moves_remaining}')
            print(f'Min distance to goal: {len(route)}')
            print(f'Moving {movechar}')
            print()
        else:
            print(f'\r[{moves_remaining} {movechar}] ', end='')

        if len(route) > moves_remaining:
            print(f'No hope of winning. Giving up.')
            log.write(f'{diff},{UNKNOWN_COST},0,0,0,0\n')
            return

        s = re.search(r'<AREA SHAPE="poly" COORDS="57,57,57,0,91,0,91,57" HREF="maze.phtml\?action=move&movedir=0&s=(\d+)"', np.content)[1]
        np.get(path, 'action=move', f'movedir={movedir}', f's={s}')
        x_cur, y_cur = x_nxt, y_nxt

def fetch_forever():
    while True:
        fetch(verbose=True)

def stats():
    data = open('fetch.log').readlines()
    data = [map(int, line.split(',')) for line in data]
    diffs = [1,2,3,4,5]
    prizes = [0, 101, 201, 501, 1501, 2501]
    steps = [0, 65, 100, 175, 225, 250]

    wins = {d: 0 for d in diffs}
    plays = {d: 0 for d in diffs}
    total_won = 0
    for diff, uk_cost, won, prize, streak, cumul in data:
        plays[diff] += 1
        if won:
            wins[diff] += 1
        total_won += prize

    for d in diffs:
        w = wins[d]
        p = plays[d]
        win_rate = w / p
        np_per_turn = prizes[d] / steps[d] * win_rate
        print(f'Difficulty {d}: Won {w} / {p} times. Rate {win_rate:.3f}. {np_per_turn:.2f} NP per turn.')
    print(f'Total won: {total_won}')

if __name__ == '__main__':
    #fetch_forever()
    stats()
