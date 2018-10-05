import re
import bisect

from lib import NeoPage
from lib import item_db
from lib import util

path = '/faerieland/employ/employment.phtml'#?type=jobs&voucher=basic&start=0'

job_re = re.compile(r'''<TR>.*?<img src='http://images.neopets.com/items/(.*?)'.*?></TD>\n<TD .*?><B>.*?</B></TD><TD .*?><B><A HREF="(.*?)">Apply for this job</B></A></TD>\n</TR>\n<TR><TD .*?><b>Find (\d+) of:</b> (.*?)<BR>.*?<B>Base Reward:</B> (.*?) NP</TD></TR>''')

def faerieland_jobs():
    np = NeoPage()
    np.get(path, 'type=jobs', 'voucher=basic')
    start = 0
    jobs_by_profit = []
    while True:
        jobs = job_re.findall(np.content)
        for image, link, count, name, prize in jobs:
            count = int(count)
            prize = util.amt(prize)
            revenue = prize * 1.25
            if len(jobs_by_profit) >= 1 and revenue < jobs_by_profit[-1][0]:
                print(f'Skipping {name}')
                continue
            price = item_db.get_price(name, image)
            profit = revenue - count * price
            print(f'Can profit by {profit}: Buy {count}x {name} ({price} NP each), turn in for {revenue}')
            bisect.insort(jobs_by_profit, (profit, name, count, link))
        if re.search('<A HREF="employment.phtml.*?">Next 10</A>', np.content):
            start += 10
            np.get(path, 'type=jobs', 'voucher=basic', f'start={start}')
        else:
            break
    print(jobs_by_profit)

if __name__ == '__main__':
    faerieland_jobs()
