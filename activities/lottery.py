import itertools
import random

from lib import NeoPage
from lib import util

path = '/games/lottery.phtml'
path_process = '/games/process_lottery.phtml'

numbers = list(range(1, 31))
N = 6
n_tickets = 20

def intersect_sorted_lists(A, B):
    i = 0
    j = 0
    ans = 0
    while i < len(A) and j < len(B):
        if A[i] > B[j]:
            j += 1
        elif A[i] < B[j]:
            i += 1
        else:
            i += 1
            j += 1
            ans += 1
    return ans

def evaluate(tickets):
    shattered_5 = set()
    shattered_4 = set()
    for ticket in tickets:
        for x in itertools.combinations(ticket, 5):
            shattered_5.add(x)
        for x in itertools.combinations(ticket, 4):
            shattered_4.add(x)
    return (len(shattered_5), len(shattered_4))

def lottery():
    numbers_left = {n:4 for n in numbers}
    tickets = []
    for _ in range(n_tickets):
        min_left = min(numbers_left.values())
        population = [k for k, v in numbers_left.items() if v > min_left]
        #population = numbers
        if len(population) < N:
            population = [k for k, v in numbers_left.items() if v >= min_left]
        ticket = tuple(sorted(random.sample(population, N)))
        tickets.append(ticket)
    print(tickets)
    print(evaluate(tickets))

    np = NeoPage()
    np.get(path)
    ref = np.referer
    for ticket in tickets:
        np.set_referer(ref)
        np.post(path_process, *[f'{x}={n}' for x, n in zip('one two three four five six'.split(), ticket)])

def stats():
    np = NeoPage()
    np.get(path)
    tbl = np.search(r'<table align=center cellpadding=3 cellspacing=0 border=0>(.*?)</table>')[0]
    rows = util.table_to_tuples(tbl)

    freqs = {i: 0 for i in range(1, 31)}
    for date, prize, winners, share, matches_needed, numbers in rows[1:]:
        nums = map(int, numbers.split(','))
        for n in nums:
            freqs[n] += 1

    for n, freq in sorted(freqs.items()):
        print(f'{n}, {freq}')

if __name__ == '__main__':
    #lottery()
    stats()
