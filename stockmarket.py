#!/usr/bin/env python3

import re
from collections import defaultdict

import lib

def stock_market():
    np = lib.NeoPage()

    # Get current stock prices
    np.get('/stockmarket.phtml')
    marquee = np.search(r'<marquee>(.*?)</marquee>')[1]
    stocks = set(re.findall(r'<b>(.*?)</b>', marquee))
    stocks_by_price = defaultdict(list)
    stock_price = {}

    for stock_line in stocks:
        symbol, price, delta = stock_line.split()
        price = int(price)
        delta = int(delta)
        stock_price[symbol] = price
        stocks_by_price[price].append(symbol)
    print(stock_price)
    print(stocks_by_price)

    # Get my portfolio
    np.get('/stockmarket.phtml?type=portfolio')

    trs = np.findall(r'<tr bgcolor=.*?>(.*?)</tr>')[0:-1:2]
    owned_stocks = {}
    for tr in trs:
        rows = re.findall(r'<td.*? align="center".*?>(.*?)</td>', tr, flags=re.DOTALL)
        symbol = re.search(r'ticker=(\w+)', rows[1])[1]
        qty = int(rows[5].strip().replace(',', ''))
        worth = qty * stock_price[symbol]
        owned_stocks[symbol] = qty

    trs = np.findall(r'<tr id=.*?>(.*?)</tr>')
    for tr in trs:
        pass

    # Sell stocks that have appreciated above threshold
    for symbol, qty in owned_stocks.items():
        if stock_price[symbol] >= 60:

    # Buy 1000 of the lowest-priced stock
    

if __name__ == '__main__':
    stock_market()
