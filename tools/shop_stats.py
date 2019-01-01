from collections import defaultdict
from lib import data as D

def main():
    shop_sales_log = open('shop_sales.log').readlines()
    data = []
    for line in shop_sales_log:
        date, buyer, rest = line.split(',', 2)
        item, revenue = rest.rsplit(',', 1)
        revenue = int(revenue)
        dd, mm, yyyy = date.split('/')
        date = f'{yyyy}-{mm}-{dd}'
        data.append((date, buyer, item, revenue))

    item_to_shop = {}
    for shop_id, items in D.store_price_data.items():
        for item in items:
            item_to_shop[item] = shop_id

    sales_by_date = defaultdict(int)
    items_by_buyer = defaultdict(list)
    sales_by_buyer = defaultdict(int)
    count_by_item = defaultdict(int)
    sales_by_shop = defaultdict(int)
    count_by_shop = defaultdict(int)
    for date, buyer, item, revenue in data:
        sales_by_date[date] += revenue
        items_by_buyer[buyer].append(item)
        sales_by_buyer[buyer] += revenue
        count_by_item[item] += 1

        if item in item_to_shop:
            shop = item_to_shop[item]
            sales_by_shop[shop] += revenue
            count_by_shop[shop] += 1
        else:
            print(f'Warning: {item} not found in any shop')

    print('Sales by date')
    for date, sales in sorted(sales_by_date.items()):
        print(f'{date}: {sales}')
    print()

    print('Top 10 buyers by revenue')
    for buyer, sales in sorted(sales_by_buyer.items(), key=lambda x:x[1])[-10:]:
        print(f'{buyer}: {sales} ({len(items_by_buyer[buyer])} items)')
    print()

    print('Top 10 buyers by volume')
    for buyer, items in sorted(items_by_buyer.items(), key=lambda x:len(x[1]))[-10:]:
        print(f'{buyer}: {len(items)} (totalling {sales_by_buyer[buyer]} NP)')
    print()

    print('Top 10 items by sale count')
    for item, count in sorted(count_by_item.items(), key=lambda x:x[1])[-10:]:
        if count > 1:
            print(f'{item}: {count}')
    print()

    print('Sales by shop')
    for shop, sales in sorted(sales_by_shop.items(), key=lambda x:x[1]):
        print(f'{shop}: {sales}')

    print(f'Num unique buyers: {len(items_by_buyer)}')
    print(f'Lifetime sales: {sum(sales_by_date.values())}')

if __name__ == '__main__':
    main()
