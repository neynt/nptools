def fetch_stats():
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
    fetch_stats()
