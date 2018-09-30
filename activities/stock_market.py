import re
from collections import defaultdict

import lib
from lib import inventory

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

    # Get my portfolio
    np.get('/stockmarket.phtml?type=portfolio')

    trs = np.findall(r'<tr bgcolor=.*?>(.*?)</tr>')[0:-1:2]
    owned_stocks = defaultdict(int)
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
            print(f'Stock Market: Should sell {symbol} @{stock_price[symbol]}')
            # TODO: Sell shares.

    # TODO: Battledome perk that reduces min price to 10
    for price in range(15, 18):
        if price in stocks_by_price:
            # Buys an amount of stock that tries to equalize your holdings in
            # each stock. For example, if BUZZ and FISH are the stocks trading
            # at 15 and you currently own 1500 BUZZ and 2000 FISH, we will buy
            # 750 BUZZ and 250 FISH to put them both at 2250.
            # TODO: This was cool to figure out but simply buying 1000 of the
            # stock you have the least of would result in roughly the same
            # thing in the long run. Maybe we should just do that.
            to_buy = stocks_by_price[price]
            to_buy_by_owned = sorted(to_buy, key=lambda x:owned_stocks[x])
            to_buy_amt = {x:0 for x in to_buy}
            stocks_seen = []
            rem = 1000

            for sym1, sym2 in zip(to_buy_by_owned, to_buy_by_owned[1:]):
                stocks_seen.append(sym1)
                max_quant = owned_stocks[sym2] - owned_stocks[sym1]
                for i,sym in enumerate(stocks_seen):
                    quant = rem // (len(stocks_seen) - i)
                    quant = min(quant, max_quant)
                    rem -= quant
                    to_buy_amt[sym] += quant
            stocks_seen.append(to_buy_by_owned[-1])

            for i,sym in enumerate(stocks_seen):
                quant = rem // (len(stocks_seen) - i)
                rem -= quant
                to_buy_amt[sym] += quant

            print(f'Stock Market: Will buy {to_buy_amt} @{price}.')
            inventory.ensure_np(price * 1000)

            for sym, amt in to_buy_amt.items():
                if amt == 0: continue
                np.get('/stockmarket.phtml?type=buy')
                _ref_ck = np.search(r"<input type='hidden' name='_ref_ck' value='(.*?)'>")[1]
                np.post('/process_stockmarket.phtml?', f'_ref_ck={_ref_ck}', 'type=buy', f'ticker_symbol={sym}', f'amount_shares={amt}')
                if np.contains('errorOuter'):
                    break
                else:
                    print(f'Stock Market: Bought {amt}x{sym} @{price}')
            if np.contains('errorOuter'):
                if np.contains('over the daily purchase limit'):
                    print('Stock Market: Already bought today.')
                elif np.contains('cannot afford'):
                    print(f'Stock Market: Could not afford {to_buy_amt} @{price}.')
                else:
                    print(f'Stock Market: Could not buy {to_buy_amt} @{price}.')
            break
    else:
        print('Stock Market: No cheap shares found.')

if __name__ == '__main__':
    stock_market()
