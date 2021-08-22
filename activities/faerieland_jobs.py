import re
import sys
import bisect

from lib import NeoPage, item_db, util, inventory, g

# TODO: Take a bunch of the item-acquisition logic out of here!

# Minimum profit to take a job.
MIN_PROFIT=2000

path = '/faerieland/employ/employment.phtml'#?type=jobs&voucher=basic&start=0'

job_re = re.compile(r'''<TR>.*?<img src='http://images.neopets.com/items/(.*?)'.*?></TD>\n<TD .*?><B>.*?</B></TD><TD .*?><B><A HREF="(.*?)">Apply for this job</B></A></TD>\n</TR>\n<TR><TD .*?><b>Find (\d+) of:</b> (.*?)<BR>.*?<B>Base Reward:</B> (.*?) NP</TD></TR>''')

def faerieland_jobs(jobs_to_do):
    np = NeoPage()
    np.get(path, 'type=jobs', 'voucher=basic')
    start = 0
    jobs_by_profit = []
    try:
        while jobs_to_do > 0:
            jobs = job_re.findall(np.content)
            has_more_pages = bool(re.search('<A HREF="employment.phtml.*?">Next 10</A>', np.content))
            for image, job_link, count, name, prize in jobs:
                count = int(count)
                prize = util.amt(prize)
                revenue = prize * 1.25
                if revenue < MIN_PROFIT:
                    print(f'Skipping {name} (can only make {revenue})')
                    continue

                price = item_db.get_price(name, image)
                profit = revenue - count * price
                print(f'Can profit by about {profit} NP: Buy {count}x {name} ({price} NP each), turn in for {revenue}')
                bisect.insort(jobs_by_profit, (profit, name, count, job_link))
                if profit < MIN_PROFIT:
                    continue
                print('Taking the job!')

                true_cost = inventory.purchase(name, image=image, budget=revenue - MIN_PROFIT, quantity=count)
                if not true_cost:
                    print(f'Failed to acquire all the items within budget')
                    continue

                # Do the job!
                np.get(f'/faerieland/employ/{job_link}')
                if 'Good job! You got all the items' in np.content:
                    prize = re.search(r'You have been paid <b>(.*?) Neopoints</b>.', np.content)[1]
                    prize = util.amt(prize)
                    print(f'Turned in {count}x {name} for {prize} NP. (Profit: {prize - true_cost})')
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
    except item_db.ShopWizardBannedException:
        return

    print(jobs_by_profit)
    print('Did not find enough appropriate jobs.')

if __name__ == '__main__':
    g.load_data()
    try:
        faerieland_jobs(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
    finally:
        g.save_data()
