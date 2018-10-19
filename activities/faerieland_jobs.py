import re
import sys
import bisect

from lib import NeoPage
from lib import item_db
from lib import util
from lib import inventory

# TODO: Take a bunch of the item-acquisition logic out of here!

# Minimum profit to take a job.
MIN_PROFIT=2000

path = '/faerieland/employ/employment.phtml'#?type=jobs&voucher=basic&start=0'

shop_item_re = re.compile(r'''<TD .*?><A href="(.*?)" .*?><img src="http://images.neopets.com/items/(.*?)" .*?></a>.*?<b>(.*?)</b><br>(.*?) in stock<br>Cost : (.*?) NP<br><br></td>''')

job_re = re.compile(r'''<TR>.*?<img src='http://images.neopets.com/items/(.*?)'.*?></TD>\n<TD .*?><B>.*?</B></TD><TD .*?><B><A HREF="(.*?)">Apply for this job</B></A></TD>\n</TR>\n<TR><TD .*?><b>Find (\d+) of:</b> (.*?)<BR>.*?<B>Base Reward:</B> (.*?) NP</TD></TR>''')

def faerieland_jobs(jobs_to_do):
    np = NeoPage()
    np.get(path, 'type=jobs', 'voucher=basic')
    start = 0
    jobs_by_profit = []
    while jobs_to_do > 0:
        jobs = job_re.findall(np.content)
        has_more_pages = bool(re.search('<A HREF="employment.phtml.*?">Next 10</A>', np.content))
        for image, job_link, count, name, prize in jobs:
            count = int(count)
            prize = util.amt(prize)
            revenue = prize * 1.25
            if revenue < MIN_PROFIT:
                print(f'Skipping {name}')
                continue

            price = item_db.get_price(name, image)
            profit = revenue - count * price
            print(f'Can profit by about {profit} NP: Buy {count}x {name} ({price} NP each), turn in for {revenue}')
            bisect.insort(jobs_by_profit, (profit, name, count, job_link))
            if profit < MIN_PROFIT:
                print(f'Skipping {name}')
                continue

            market = item_db.get_market(name, image)
            print(f'Market is: {market[:3]}')
            true_cost = 0
            count_left = count
            buy_nps = []
            for price, stock, link in market:
                np2 = NeoPage()
                np2.get(link)
                buy_link, image, name, in_stock, cost = shop_item_re.search(np2.content).groups()
                in_stock = util.amt(in_stock)
                cost = util.amt(cost)
                print(f'{name} {in_stock} {price} {cost} {count_left}')
                if cost <= price:
                    to_buy = min(in_stock, count_left)
                    true_cost += cost * to_buy
                    count_left -= to_buy
                    buy_nps.append((np2, buy_link, to_buy))
                    if count_left <= 0:
                        break
            true_profit = revenue - true_cost
            print(f'True profit: {true_profit}')
            if true_profit < MIN_PROFIT:
                print(f'Skipping {name}')
                continue

            print(buy_nps)

            inventory.ensure_np(true_cost)
            for np2, buy_link, to_buy in buy_nps:
                referer = np2.referer
                for _ in range(to_buy):
                    print(f'Buying {name} from {buy_link}')
                    np2.set_referer(referer)
                    np2.get(f'/{buy_link}')

            # Do the job!
            np.get(f'/faerieland/employ/{job_link}')
            if 'Good job! You got all the items' in np.content:
                prize = re.search(r'You have been paid <b>(.*?) Neopoints</b>.', np.content)[1]
                prize = util.amt(prize)
                print(f'Turned in {count}x {name} for {prize} NP. (Profit: {true_profit})')
            elif 'You got the job!' in np.content:
                print(f'Job was not completed before applying? TODO')
                print(np.last_file_path)
                return
            else:
                print(f'Error applying for job. TODO')
                print(np.last_file_path)
                return
            jobs_to_do -= 1
            if jobs_to_do <= 0:
                return

        if has_more_pages:
            start += 10
            np.get(path, 'type=jobs', 'voucher=basic', f'start={start}')
        else:
            break
    print(jobs_by_profit)
    print('Did not find enough appropriate jobs.')

if __name__ == '__main__':
    faerieland_jobs(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
