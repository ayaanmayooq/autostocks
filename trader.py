import config

import trade_start
import grapher
from paper_test import *

import pyotp
import robin_stocks.robinhood as rh
import datetime as dt
import time
import pandas as pd

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
    market = True
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

def get_cash():
    rh_cash = rh.account.build_user_profile()

    cash = float(rh_cash['cash'])
    equity = float(rh_cash['equity'])
    return cash, equity

def get_holdings_and_bought_price(stocks):
    holdings = {stocks[i]: 0 for i in range(0, len(stocks))}
    bought_price = {stocks[i]: 0 for i in range(0, len(stocks))}
    rh_holdings = rh.account.build_holdings()

    for stock in stocks:
        try:
            holdings[stock] = int(float((rh_holdings[stock]['quantity'])))
            bought_price[stock] = float((rh_holdings[stock]['average_buy_price']))
        except:
            holdings[stock] = 0
            bought_price[stock] = 0

    return holdings, bought_price

def build_dataframes(df_trades, trade_dict, df_prices, price_dict):
    time_now = str(dt.datetime.now().time())[:8]
    df_trades.loc[time_now] = trade_dict
    df_prices.loc[time_now] = price_dict
    return df_trades, df_prices


if __name__ == "__main__":
    login(1)

    stocks = ['TSLA', 'AMZN', 'GOOGL']

    print('stocks:', stocks)
    # cash, equity = get_cash()
    # dummy here ...
    initial_cash = 1000
    portfolio = Portfolio(initial_cash)

    strat = trade_start.Trader(stocks)
    strat.start_runtime()

    trade_dict = {stocks[i]: 0 for i in range(0, len(stocks))}
    price_dict = {stocks[i]: 0 for i in range(0, len(stocks))}
    df_trades = pd.DataFrame(columns=stocks)
    df_prices = pd.DataFrame(columns=stocks)

    while open_market():
        strat.update_runtime()

        prices = rh.stocks.get_latest_price(stocks)
        # holdings, bought_price = get_holdings_and_bought_price(stocks)
        # dummy here ...
        holdings = portfolio.holdings
        print(30 * '-')
        print('holdings:')
        for holding in holdings:
            print('{} = ${}'.format(holding.stock, holding.bought_price))
        print(30*'-')

        for stock, price in zip(stocks, prices):
            price = float(price)
            print('{} = ${}'.format(stock, price))

            trade = strat.trade_option(stock, price)
            print('trade:', trade)

            if trade == "BUY":
                allowable_holdings = int(portfolio.cash_balance / price)
                if allowable_holdings > 0 and not portfolio.get_holding(stock):
                    portfolio.buy(stock, 1, price, dt.datetime.now())
            elif trade == "SELL":
                if portfolio.get_holding(stock):
                    portfolio.sell(stock, 1, price, dt.datetime.now())

            price_dict[stock] = price
            if portfolio.get_holding(stock) and trade != "SELL":
                trade = "HOLD"
            elif not portfolio.get_holding(stock) and trade != "BUY":
                trade = "WAIT"
            trade_dict[stock] = trade

            # if trade == "BUY":
            #     allowable_holdings = int((cash / 10) / price)
            #     if allowable_holdings > 5 and holdings[stock] == 0:
            #         buy(stock, allowable_holdings)
            # elif trade == "SELL":
            #     if holdings[stock] > 0:
            #         sell(stock, holdings[stock], price)

            # price_dict[stock] = price
            # if holdings[stock] > 0 and trade != "SELL":
            #     trade = "HOLD"
            # elif holdings[stock] == 0 and trade != "BUY":
            #     trade = "WAIT"
            # trade_dict[stock] = trade

        df_trades, df_prices = build_dataframes(df_trades, trade_dict, df_prices, price_dict)
        grapher.active_graph(grapher.normalize(df_prices), df_trades)

        print("Portfolio value:", portfolio.calculate_portfolio_value())

        time.sleep(30)
