import alpaca_trade_api as tradeapi

def setAlpacaApi(api_key, secret_key):
    global api
    api = tradeapi.REST(
        api_key,
        secret_key,
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
    bars = barset[sym]
    return bars

def getCurrentPrice(sym):
    bars = getHistoricalPrice(sym, 'day', 1)
    if len(bars) == 0:
        return -1
    day_close = bars[0].c
    return day_close

def getMarketOpenPrice(sym):
    bars = getHistoricalPrice(sym, 'day', 1)
    if len(bars) == 0:
        return -1
    openPrice = bars[0].o
    return openPrice


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

    # Check when the market was open on Dec. 1, 2018
    calendar = api.get_calendar(start=date, end=date)[0]
    return calendar

def getPercentChange(sym, time, limit):
    bars = getHistoricalPrice(sym, time, limit)
    if len(bars) == 0:
        return [0, -1]
    open = bars[0].o
    close = bars[-1].c
    percent_change = (close - open) / open * 100
    return [percent_change, close]

def getWeeklyChange(sym):
    return getPercentChange(sym, 'day', 5)

def getDailyChange(sym):
    return getPercentChange(sym, 'day', 1)