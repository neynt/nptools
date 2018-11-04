# Old unused code for Shapeshifter.

# A grid is a list of R lists of size C.
# A shape is a big-endian encoded integer. Hopefully it's faster?
def grid_to_shape(grid, N, R, C):
    data = 0
    GR = len(grid)
    GC = len(grid[0])
    b = 1
    for r in range(R):
        for c in range(C):
            data += b * (grid[r][c] if 0 <= r < GR and 0 <= c < GC else 0)
            b *= N
    return data

def shape_to_grid(shape, N, R, C):
    grid = []
    for r in range(R):
        row = []
        for c in range(C):
            row.append(data % N)
            data //= N
        grid.append(row)
    return grid

def print_shape(shape, N, R, C):
    for r in range(R):
        for c in range(C):
            print(shape % N, end=' ')
            shape //= N
        print()

def move_shape(s1, N, C, r, c):
    return s1 * N**(c + C*r)

def add_shapes(s1, s2, N):
    res = 0
    b = 1
    while s1 or s2:
        res += b * ((s1 % N + s2 % N) % N)
        b *= N
        s1 //= N
        s2 //= N
    return res

# TODO: dedup with above somehow
def sub_shapes(s1, s2, N):
    res = 0
    b = 1
    while s1 or s2:
        res += b * ((s1 % N - s2 % N) % N)
        b *= N
        s1 //= N
        s2 //= N
    return res

def gen_prevs(shapes, N, R, C):
    n_states = N ** (R * C)
    prevs = []
    prevs.append({0: (0, 0, 0)})

    print(f'Finding all possible shapes for {len(shapes)} pieces.')

    # A straightforward DP.
    for i, (shape, SR, SC) in enumerate(shapes):
        shifted_shapes = []
        for r in range(R - SR + 1):
            for c in range(C - SC + 1):
                shifted_shapes.append((move_shape(shape, N, C, r, c), r, c))
        prev = {}
        for old_shape, v in prevs[-1].items():
            if v == None: continue
            for shifted_shape, r, c in shifted_shapes:
                shape_ = add_shapes(old_shape, shifted_shape, N)
                if shape_ not in prev:
                    prev[shape_] = (old_shape, r, c)
        print(f'Smashed piece {i+1}/{len(shapes)}. New difficulty is {len(prev)}')
        prevs.append(prev)
    
    return prevs

def old_main_stuff():
    # prevs[i] is a dictionary.
    # Keys are states reachable after placing shapes[i - 1].
    # Values are (previous state, r, c).
    # Once fully populated, this lets us trace our steps back to the beginning
    # and obtain each step of the solution.
    prevs = [{((0,) * C,) * R: None}]
    n_shapes = len(shapes)
    n_half1 = (n_shapes + 1) // 2
    n_half2 = n_shapes - n_half1
    half1 = shapes[:n_half1]
    half2 = shapes[n_half1:]
    prevs1 = gen_prevs(half1, N, R, C)
    prevs2 = gen_prevs(half2, N, R, C)

    goal1 = None
    goal2 = None
    for shape1, v in prevs1[-1].items():
        if not v: continue
        shape2 = sub_shapes(goal_shape, shape1, N)
        if shape2 in prevs2[-1]:
            goal1 = shape1
            goal2 = shape2
            break
    else:
        print('It seems there is no solution???')
        return
    pass

def backtrace(prevs, goal_shape):
    positions = []
    shape = goal_shape
    for prev in reversed(prevs[1:]):
        (shape_, r, c) = prev[shape]
        positions.append((r, c))
        shape = shape_
    return list(reversed(positions))


# Let's SMT Solve!
# Our variables are:
# g_r_c: Total contribution to position (r, c) on the board
# p_i_r_c: Whether or not to place piece i in position (r, c)
# TODO: Should we instead use integer theories to solve directly for the (r, c)
# of each piece?
# ANSWER: No, SMT solvers suck.

import z3
def sat_solve(goal_grid, shapes, N):
    R = len(goal_grid)
    C = len(goal_grid[0])
    #goal_vars = [[z3.Int(f'g_{r}_{c}') for c in range(C)] for r in range(R)]
    s = z3.Solver()
    #for r, (grid_row, var_row) in enumerate(zip(goal_grid, goal_vars)):
    #    for c, (val, var) in enumerate(zip(grid_row, var_row)):
    #        s.add(var == val)

    contributors = defaultdict(list)

    all_put_vars = []
    for i, shape in enumerate(shapes):
        SR = len(shape)
        SC = len(shape[0])
        put_vars = []
        put_vars_with_coords = []
        for r in range(R - SR + 1):
            for c in range(C - SC + 1):
                put_var = z3.Int(f'p_{i}_{r}_{c}')
                put_vars.append((put_var, r, c))
                s.add(z3.Or(put_var == 0, put_var == 1))
                for sr, shape_row in enumerate(shape):
                    for sc, shape_val in enumerate(shape_row):
                        if shape_val: contributors[(r + sr, c + sc)].append(put_var)

        just_vars = [v for v, _, _ in put_vars]
        s.add(z3.Sum(just_vars) == 1)
        all_put_vars.append(put_vars)

    for (r, c), put_vars in contributors.items():
        s.add(z3.Sum(put_vars) % N == goal_grid[r][c])

    print(s.check())
    model = s.model()
    print(model)
    coords = []
    for put_vars in all_put_vars:
        for (var, r, c) in put_vars:
            if model[var] == 1:
                coords.append((r, c))
                break
    print(coords)
    return coords
