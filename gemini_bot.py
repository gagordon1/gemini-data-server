
from dotenv import dotenv_values
config = dotenv_values(".env")

import json
from time import sleep

price = 0.0
states = ["bid", "waiting_to_fill", "ask", "waiting_to_fill"]

class GeminiBot:
    def __init__(self, ticker, amountToBuy, amountToSell):
        self.ticker = ticker
        self.amountToBuy = amountToBuy
        self.amountToSell = amountToSell
        self.state = 0
        self.bid_order_price = 0
        self.sell_order_price = 0
        self.count = 0
        self.transactions = []
        self.timestamp = 0
        self.lastTradePrice = 0

    """
    Check if an order has been placed
    If so, see how much of the order is left to be filled
    """
    def order_remaining(self):
        pass

    """
    If an order has yet to be filled cancel it
    """
    def cancel_order(self):
        pass

    """
    ticker : str
    type : "bid" | "ask"
    price : float
    amount : float
    returns boolean : true if successful, false otherwise
    """
    def maker_or_cancel_order(self, type, price, amount):
        print("Limit or cancel {} order placed: {}{} at ${}").format(
                type, amount, self.ticker, price)

    """
    ws : WebSocketApp
    message : json string
    Algorithm:
        0 (decide to buy or sell):
            if (amountToBuy > amountToSell)
                move to state 1
            else
                move to state 3
        1 (buy):
            place maker or cancel order for last_price * (1 - margin)
            set bid_order_price = last_price * (1 - margin)
            move to state 2
        2 (wait after buy)
            if (order filled)
                decrement amount to buy
                move to state 0
            if (last_price > bid_order_price * (1 + margin))
                decrement amount to buy if partially filled
                move to state 0
        3 (sell)
            place maker or cancel order for last_price * (1 + margin)
            set sell_order_price = last_price * (1 + margin)
            move to state 4

        4 (wait after sell)
            if (order filled)
                decrement amount to sell
                move to state 0
            if (last_price < bid_order_price * (1-margin))
                decrement amonunt to sell if partially filled
                move to state 0

    """
    def strategy1(self, ws, message):
        #BTC SPREAD IS ~ .0002 * price

        # UPDATE BOT STATE
        if self.state == 0:
            pass

        elif self.state == 1:
            print("Making buy order...")
            pass

        elif self.state == 2:
            print("Waiting for buy order to fill...")

        elif self.state == 3:
            print("Making sell order")

        elif self.state == 4:
            print("Waiting for sell to fill...")


        elif self.state == 5:
            print("Safe debugging state...")
            #safe debugging state

if __name__ == '__main__':
    g = GeminiBot("btcusd", .0005, .0005)
