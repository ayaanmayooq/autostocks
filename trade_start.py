import pandas as pd
import time

import robin_stocks.robinhood as rh

class Trader:
    def __init__(self, stocks):
        self.stocks = stocks

        self.sma_hour = {stocks[i]: 0 for i in range(0, len(stocks))}

        # Exponential Moving Averages
        self.ema_9 = {stocks[i]: 0 for i in range(0, len(stocks))}
        self.ema_21 = {stocks[i]: 0 for i in range(0, len(stocks))}
        self.ema_50 = {stocks[i]: 0 for i in range(0, len(stocks))}

        # MACD indicator
        self.macd_line = {stocks[i]: 0 for i in range(0, len(stocks))}
        self.macd_signal_line = {stocks[i]: 0 for i in range(0, len(stocks))}

        self.start_time = 0
        self.run_time = 0
        self.buffer = 0.0001 # 0.05%

        self.price_sma_hour = {stocks[i]: 0 for i in range(0, len(stocks))}

    def update_runtime(self):
        self.run_time = time.time() - self.start_time

    def start_runtime(self):
        self.start_time = time.time()  # Record the start time

    def get_runtime(self):
        return self.run_time

    def get_historical_prices(self, stock, span):
        span_interval = {'day': '5minute', 'week': '10minute', 'month': 'hour', '3month': 'hour', 'year': 'day',
                         '5year': 'week'}
        interval = span_interval[span]

        historical_data = rh.stocks.get_stock_historicals(stock, interval=interval, span=span, bounds='extended')

        df = pd.DataFrame(historical_data)

        dates_times = pd.to_datetime(df.loc[:, 'begins_at'])
        close_prices = df.loc[:, 'close_price'].astype('float')

        df_price = pd.concat([close_prices, dates_times], axis=1)
        df_price = df_price.rename(columns={'close_price': stock})
        df_price = df_price.set_index('begins_at')

        return df_price

    def get_sma(self, stock, df_prices, window=12):
        sma = df_prices.rolling(window=window, min_periods=window).mean()
        sma = round(float(sma[stock].iloc[-1]), 4)
        return sma

    def get_ema(self, stock, df_prices, span=9):
        ema = df_prices[stock].ewm(span=span, adjust=False).mean().iloc[-1]
        return round(ema, 4)

    def calculate_macd(self, stock, df_prices, short_window=12, long_window=26, signal_window=9):
        short_ema = df_prices[stock].ewm(span=short_window, adjust=False).mean()
        long_ema = df_prices[stock].ewm(span=long_window, adjust=False).mean()
        macd_line = short_ema - long_ema
        signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line.iloc[-1], signal_line.iloc[-1], histogram

    def get_price_sma(self, price, sma):
        price_sma = round(price / sma, 4)
        return price_sma

    def trade_option(self, stock, price):
        # gets new sma_hour every 5min
        if (self.run_time//60) % (5) == 0:
            df_historical_prices = self.get_historical_prices(stock, span='day')
            self.sma_hour[stock] = self.get_sma(stock, df_historical_prices[-12:], window=12)

            # Calculating required EMAs for day trading (every 5 mins)
            self.ema_9[stock] = self.get_ema(stock, df_historical_prices, span=9)
            self.ema_21[stock] = self.get_ema(stock, df_historical_prices, span=21)
            self.ema_50[stock] = self.get_ema(stock, df_historical_prices, span=50)

            # Calculating MACD lines
            self.macd_line[stock], self.macd_signal_line[stock], _ = self.calculate_macd(stock, df_historical_prices)

        self.price_sma_hour[stock] = self.get_price_sma(price, self.sma_hour[stock])
        p_sma = self.price_sma_hour[stock]

        i1 = "BUY" if self.price_sma_hour[stock] < (1.0 - self.buffer) else "SELL" if self.price_sma_hour[stock] > (
                    1.0 + self.buffer) else "NONE"

        ema_i1 = 0
        if price / self.ema_9[stock] > (1 + self.buffer):
            ema_i1 += 1
        else:
            if price / self.ema_9[stock] < (1 - self.buffer):
                ema_i1 -= 1
            else:
                ema_i1 -= 0

        if price / self.ema_21[stock] > (1 + self.buffer):
            ema_i1 += 1
        else:
            if price / self.ema_21[stock] < (1 - self.buffer):
                ema_i1 -= 1
            else:
                ema_i1 -= 0

        if price / self.ema_50[stock] > (1 + self.buffer):
            ema_i1 += 1
        else:
            if price / self.ema_50[stock] < (1 - self.buffer):
                ema_i1 -= 1
            else:
                ema_i1 -= 0

        # macd_i = 0
        # if self.macd_line[stock] / self.macd_signal_line[stock] > (1 + self.buffer):
        #     macd_i = 1
        # elif self.macd_line[stock] / self.macd_signal_line[stock] < (1 - self.buffer):
        #     macd_i = -1
        # else:
        #     macd_i = 0

        macd_value = self.macd_line[stock]
        signal_value = self.macd_signal_line[stock]

        buffer_percentage = 0.5
        buffer = (buffer_percentage / 100) * self.macd_signal_line[stock]

        if macd_value > signal_value and macd_value - signal_value > buffer:
            macd_i = 1  # MACD line crossed above signal line with buffer
        elif macd_value < signal_value and signal_value - macd_value > buffer:
            macd_i = -1  # MACD line crossed below signal line with buffer
        else:
            macd_i = 0  # No significant crossover or buffer not met

        print("EMA val:", stock, ema_i1)
        print("MACD val:", stock, macd_i)

        if ema_i1 > 0 and macd_i > 0:
            trade = "BUY"
        elif ema_i1 < 0 and macd_i < 0:
            trade = "SELL"
        else:
            trade = "HOLD"

        return trade
