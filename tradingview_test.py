from tradingview_ta import TA_Handler, Interval, Exchange

tesla = TA_Handler(
    symbol="GOOGL",
    screener="america",
    exchange="NASDAQ",
    interval=Interval.INTERVAL_1_DAY
)
while True:
    x = tesla.get_analysis()
    print(x.indicators['MACD.macd'])
print(tesla.get_analysis().summary)
# Example output: {"RECOMMENDATION": "BUY", "BUY": 8, "NEUTRAL": 6, "SELL": 3}