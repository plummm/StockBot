import alpaca_trade_api as tradeapi

api = tradeapi.REST(
        'PK7UFDY1AW3S7YPWSJMO',
        'ITFjOhzWquWT5dOka5igVfHfIkwfuhELKXKluzHx',
        'https://paper-api.alpaca.markets'
    )

def getAccountInfo():

    # Get our account information.
    account = api.get_account()

    # Check if our account is restricted from trading.
    if account.trading_blocked:
        print('Account is currently restricted from trading.')

    # Check how much money we can use to open new positions.
    print('${} is available as buying power.'.format(account.buying_power))

def getGainAndLoss():
    account = api.get_account()

    # Check our current balance vs. our balance at the last market close
    balance_change = float(account.equity) - float(account.last_equity)
    print(f'Today\'s portfolio balance change: ${balance_change}')

def getHistoricalPrice(sym, time, limit):
    barset = api.get_barset(sym, time, limit=limit)
    aapl_bars = barset[sym]

    # See how much AAPL moved in that timeframe.
    week_open = aapl_bars[0].o
    week_close = aapl_bars[-1].c
    percent_change = (week_close - week_open) / week_open * 100
    print('{} moved {}% over the last 5 days'.format(sym, percent_change))

def getListOfAssets():
    active_assets = api.list_assets(status='active')

    # Filter the assets down to just those on NASDAQ.
    nasdaq_assets = [a for a in active_assets if a.exchange == 'NASDAQ']
    print(nasdaq_assets)

def place_new_market_order(sym, qty, side):
    api.submit_order(
        symbol=sym,
        qty=qty,
        side=side,
        type='market',
        time_in_force='gtc'
    )


def getMarketCalendar(date):
    clock = api.get_clock()
    print('The market is {}'.format('open.' if clock.is_open else 'closed.'))

    # Check when the market was open on Dec. 1, 2018
    calendar = api.get_calendar(start=date, end=date)[0]
    return calendar