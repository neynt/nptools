from collections import defaultdict

def parse_num(s):
    if s == 'two': return 2
    return int(s)

stat_changes = defaultdict(list)
colour_changes = []
gender_changes = 0
for orig_line in open('lab_ray.log').readlines():
    line = orig_line.strip()
    if line.endswith(':('):
        line = line[:-2].strip()
    while line.endswith('!'):
        line = line[:-1].strip()
    tok = line.split()
    if 'gains' in line or 'loses' in line:
        amt = parse_num(tok[7])
        stat = ' '.join(tok[8:])
        if 'loses' in line: amt = -amt
        stat_changes[stat].append(amt)
    elif 'changes colour' in line:
        new_colour = ' '.join(tok[9:])
        colour_changes.append(new_colour)
    elif 'changes gender' in line:
        gender_changes += 1
    else:
        print('Unknown effect: ' + orig_line.strip())

print('Total stat changes:')
for stat, changes in stat_changes.items():
    print(f'{stat}: {sum(changes)} ({changes})')
