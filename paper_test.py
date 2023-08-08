class Holding:
    def __init__(self, stock, quantity, bought_price):
        self.stock = stock
        self.quantity = quantity
        self.bought_price = bought_price
        self.current_price = 0.0  # Retrieve from real-time data

    def calculate_value(self):
        return self.quantity * self.bought_price

class Trade:
    def __init__(self, holding, quantity, price, timestamp, is_buy):
        self.holding = holding
        self.quantity = quantity    # Involved in the trade
        self.price = price  # At the time value of the stock
        self.timestamp = timestamp
        self.is_buy = is_buy

    def calculate_value(self):
        return self.quantity * self.price

    def display_trade(self):
        buy_or_sell = "Buy" if self.is_buy else "Sell"
        print(f"{buy_or_sell}: {self.quantity} {self.holding.stock} at {self.price} per share")

class Portfolio:
    def __init__(self, cash_balance):
        self.holdings = []
        self.trades = []
        self.cash_balance = cash_balance

    def add_trade(self, trade):
        self.trades.append(trade)

    def calculate_portfolio_value(self):
        total_value = sum(holding.calculate_value() for holding in self.holdings) + self.cash_balance
        return total_value

    def calculate_profit_loss(self, initial_investment):
        return self.calculate_portfolio_value() - initial_investment

    def display_portfolio_summary(self):
        for trade in self.trades:
            trade.display_trade()
        print(f"Cash Balance: {self.cash_balance}")
        print(f"Total Portfolio Value: {self.calculate_portfolio_value()}")

    def buy(self, symbol, quantity, price, timestamp):
        total_cost = quantity * price
        if total_cost <= self.cash_balance:
            existing_holding = self.get_holding(symbol)
            if existing_holding:
                existing_holding.quantity += quantity
            else:
                new_holding = Holding(symbol, quantity, price)
                self.holdings.append(new_holding)

            trade = Trade(existing_holding if existing_holding else new_holding, quantity, price, timestamp, True)
            self.trades.append(trade)
            self.cash_balance -= total_cost
            print("Buy executed:", quantity, symbol, "at", price)

    def sell(self, symbol, quantity, price, timestamp):
        existing_holding = self.get_holding(symbol)
        if existing_holding and existing_holding.quantity >= quantity:
            existing_holding.quantity -= quantity
            trade = Trade(existing_holding, quantity, price, timestamp, False)
            self.trades.append(trade)
            self.holdings.remove(existing_holding)
            self.cash_balance += quantity * price
            print("Sell executed:", quantity, symbol, "at", price)
        else:
            print("Insufficient quantity to sell.")

    def get_holding(self, stock):
        for holding in self.holdings:
            if holding.stock == stock:
                return holding
        return None

# Example usage:
# initial_cash = 10000
# portfolio = Portfolio(initial_cash)
#
# # Simulate trading actions
# portfolio.buy("AAPL", 10, 150, "2023-08-01 10:00:00")
# portfolio.sell("AAPL", 5, 160, "2023-08-02 14:30:00")
#
# # Display portfolio information
# for holding in portfolio.holdings:
#     print("Holding:", holding.stock, holding.quantity, "shares")
#
# for trade in portfolio.trades:
#     trade.display_trade()
#
# print("Cash Balance:", portfolio.cash_balance)


