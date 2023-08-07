import config

import pyotp
import robin_stocks.robinhood as rh
import datetime as dt
import time


def login(days):
    login_expiry = 60 * 60 * 24 * days

    totp = pyotp.TOTP(config.MFA).now()
    #print("Current OTP:", totp)

    rh.authentication.login(username=config.USERNAME,
                            password=config.PASSWORD,
                            expiresIn=login_expiry,
                            scope='internal',
                            by_sms=False,
                            store_session=True,
                            mfa_code=totp)


def logout():
    rh.authentication.logout()


def open_market():
    market = False
    time_now = dt.datetime.now().time()

    market_open = dt.time(9, 30, 0)
    market_close = dt.time(15, 59, 59)

    if market_open < time_now < market_close:
        market = True
    else:
        print(20 * '#')
        print('Market is closed')
        print(20 * '#')

    return market


if __name__ == "__main__":
    login(1)

    stocks = ['TSLA', 'AMZN', 'GOOGL']

    while open_market():
        prices = rh.stocks.get_latest_price(stocks)

        print("Time:", dt.datetime.now().time())
        for stock, price in zip(stocks, prices):
            print(stock, '-', price)
        print('\n', 30*'#', '\n')

        time.sleep(1)
