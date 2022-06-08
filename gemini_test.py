
from dotenv import dotenv_values
config = dotenv_values(".env")

import json
import ssl
import websocket
from threading import Thread
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

    """
    ticker : str
    type : "bid" | "ask"
    price : float
    amount : float
    returns boolean : true if successful, false otherwise
    """
    def maker_or_cancel_order(self, type, price, amount):
        while True:
            sleep(1)
            print(amount)

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
        data = json.loads(message)
        print(data)
        # thread = Thread(target = self.maker_or_cancel_order, args = ("bid", 10, 10))
        # thread.start()
        if self.state == 0:
            if self.amountToBuy > self.amountToSell:
                self.state = 1
            self.state = 3

        elif self.state == 1:
            pass

        elif self.state == 2:
            pass

        elif self.state == 3:
            

        elif self.state == 4:
            pass

    """
    Monitors trades for the object's specified ticker and runs self.on_message
    at every update
    """
    def run_forever(self):
        ws = websocket.WebSocketApp(
            "wss://api.gemini.com/v1/marketdata/{}?trades=true".format(self.ticker),
            on_message=self.strategy1)
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

GeminiBot("btcusd", 10, 10).run_forever()
