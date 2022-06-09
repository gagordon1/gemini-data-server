
from dotenv import dotenv_values
config = dotenv_values(".env")

import requests
import json
from time import sleep
import base64
import hmac
import hashlib
import datetime, time

BASE_URL = "https://api.gemini.com/v1"

TICKER_INFO_ENDPOINT = "/pubticker/"

NEW_ORDER_ENDPOINT = "/order/new"

ORDER_STATUS_ENDPOINT = "/orders"

PAST_TRADES_ENDPOINT = "/mytrades"

CANCEL_ALL_ORDERS_ENDPOINT = "/order/cancel/all"




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
        self.end_condition_met = False
        self.order_history = []
        self.nonce = int(time.time()*1000)
        self.lowest_ask = 0
        self.highest_bid = 0
        self.last_price = 0

    def nonce_up(self):
        self.nonce += 1
    """
    returns last price, lowest ask, highest bid for the object's ticker
    """
    def get_ticker_info(self):
        self.nonce_up()


        try:
            url = BASE_URL + TICKER_INFO_ENDPOINT + self.ticker
            response = requests.get(url)
            data = response.json()
            return float(data["last"]), float(data["ask"]), float(data["bid"])
        except Exception as e:
            print(e)
    """
    Gets statuses of open orders or returns False on error
    """
    def get_order_statuses(self):
        self.nonce_up()
        try:
            gemini_api_key = config["GEMINI_TRADING_API_KEY"]
            gemini_api_secret = config["GEMINI_TRADING_API_SECRET"].encode()


            payload = {
                "nonce": self.nonce,
                "request": "/v1/orders"
            }

            url = BASE_URL + ORDER_STATUS_ENDPOINT
            encoded_payload = json.dumps(payload).encode()
            b64 = base64.b64encode(encoded_payload)
            signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()

            request_headers = { 'Content-Type': "text/plain",
                                'Content-Length': "0",
                                'X-GEMINI-APIKEY': gemini_api_key,
                                'X-GEMINI-PAYLOAD': b64,
                                'X-GEMINI-SIGNATURE': signature,
                                'Cache-Control': "no-cache" }
            response = requests.post(url,
                            data=None,
                            headers=request_headers)

            orders = response.json()
            return orders
        except Exception as e:
            print(e)
            return False

    """
    Gets statuses of closed orders or returns False on error
    """
    def get_past_trades(self):
        self.nonce_up()
        print("getting past trades")
        try:
            gemini_api_key = config["GEMINI_TRADING_API_KEY"]
            gemini_api_secret = config["GEMINI_TRADING_API_SECRET"].encode()



            payload = {
                "nonce": self.nonce,
                "request":  "/v1/mytrades",
                "symbol" : self.ticker,
                "limit_trades" : 10
            }

            url = BASE_URL + PAST_TRADES_ENDPOINT
            encoded_payload = json.dumps(payload).encode()
            b64 = base64.b64encode(encoded_payload)
            signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()

            request_headers = { 'Content-Type': "text/plain",
                                'Content-Length': "0",
                                'X-GEMINI-APIKEY': gemini_api_key,
                                'X-GEMINI-PAYLOAD': b64,
                                'X-GEMINI-SIGNATURE': signature,
                                'Cache-Control': "no-cache" }
            response = requests.post(url,
                            data=None,
                            headers=request_headers)

            orders = response.json()
            return orders
        except Exception as e:
            print(e)
            return False


    """
    Check if exactly one ticker in our order history is open
    If so, see how much of the order is left to be filled
    return amount_remaining, original_amount
    otherwise
    print an error message and return False

    """
    def get_order_status(self):
        try:
            orders = self.get_order_statuses()

            if len(orders) == 0:
                #CHECK IF ANY ORDERS IN ORDER HISTORY HAVE EXECUTED
                recent_trades = self.get_past_trades()
                for order in self.order_history:
                    if float(order["amount_remaining"]) > 0 and not order["cancelled"]:
                        for o in recent_trades:
                            if o["order_id"] == order["id"]:
                                order["amount_remaining"] = 0.0
                                print("trade has been executed")
                                return 0.0, float(order["original_amount"])
                return False
            elif len(orders) == 1:
                order = orders[0]
                #check that order is in this instance's order history
                found = False
                for o in self.order_history:
                    if o["id"] == order["id"]:
                        found = True
                if not found:
                    return False
                print("remaining_amount: {}".format(order["remaining_amount"]))
                return float(order["remaining_amount"]), float(order["original_amount"])
            else:
                return False


        except Exception as e:
            print(e)

    """
    Cancel open orders
    Returns True if successfully canceled false otherwise
    """
    def cancel_active_orders(self):
        self.nonce_up()
        print("canceling orders")
        try:
            gemini_api_key = config["GEMINI_TRADING_API_KEY"]
            gemini_api_secret = config["GEMINI_TRADING_API_SECRET"].encode()

            t = datetime.datetime.now()
            payload_nonce =  str(int(time.mktime(t.timetuple())*1000))

            payload = {
                "nonce": self.nonce,
                "request": "/v1/order/cancel/all"
            }

            url = BASE_URL + CANCEL_ALL_ORDERS_ENDPOINT
            encoded_payload = json.dumps(payload).encode()
            b64 = base64.b64encode(encoded_payload)
            signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()

            request_headers = { 'Content-Type': "text/plain",
                                'Content-Length': "0",
                                'X-GEMINI-APIKEY': gemini_api_key,
                                'X-GEMINI-PAYLOAD': b64,
                                'X-GEMINI-SIGNATURE': signature,
                                'Cache-Control': "no-cache" }
            response = requests.post(url,
                            data=None,
                            headers=request_headers)

            result = response.json()
            print(result)
            if result["result"] == "ok":
                for order in self.order_history:
                    if (not order["cancelled"]) and float(order["amount_remaining"]) > 0 :
                        order["cancelled"] = True
                return True
            return False
        except Exception as e:
            print(e)
            return False

    """
    ticker : str
    type : "bid" | "ask"
    price : float
    amount : float
    returns boolean : true if successful, "is_cancelled" if the trade was cancelled
                on submit (it would have been a taker), false otherwise
    """
    def maker_or_cancel_order(self, type, price, amount):
        self.nonce_up()
        print("Placing limit {} order".format(type))
        price = round(price, 2)

        try:

            gemini_api_key = config["GEMINI_TRADING_API_KEY"]
            gemini_api_secret = config["GEMINI_TRADING_API_SECRET"].encode()

            t = datetime.datetime.now()
            payload_nonce =  str(int(time.mktime(t.timetuple())*1000))

            side = "buy"
            if type == "ask":
                side = "sell"


            payload = {
               "request": "/v1/order/new",
                "nonce": self.nonce,
                "symbol": self.ticker,
                "amount": str(amount),
                "price": str(price),
                "side": side,
                "type": "exchange limit",
                "options": ["maker-or-cancel"]
            }

            url = BASE_URL + NEW_ORDER_ENDPOINT
            encoded_payload = json.dumps(payload).encode()
            b64 = base64.b64encode(encoded_payload)
            signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()

            request_headers = { 'Content-Type': "text/plain",
                                'Content-Length': "0",
                                'X-GEMINI-APIKEY': gemini_api_key,
                                'X-GEMINI-PAYLOAD': b64,
                                'X-GEMINI-SIGNATURE': signature,
                                'Cache-Control': "no-cache" }
            response = requests.post(url,
                            data=None,
                            headers=request_headers)

            new_order = response.json()
            if "is_cancelled" in new_order:
                if new_order["is_cancelled"]:
                    return "is_cancelled"
            if "is_live" in new_order and new_order["is_live"]:
                print("Limit or cancel {} order placed: {}{} at ${}".format(
                        type, amount, self.ticker, price))
                self.order_history.append(
                    {
                        "id" : new_order["order_id"],
                        "symbol" : new_order["symbol"],
                        "side" : new_order["side"],
                        "price" : new_order["price"],
                        "timestamp" : new_order["timestamp"],
                        "original_amount" :new_order["original_amount"],
                        "amount_remaining" : new_order["remaining_amount"],
                        "cancelled" : False
                    }
                )

                return True
            else:
                print(new_order)
                return False
        except Exception as e:
            print(e)
            return False





    """
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
            if (last_price > bid_order_price * (1 + 2*margin))
                cancel order
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
            if (last_price < bid_order_price * (1-2*margin))
                cancel order
                decrement amonunt to sell if partially filled
                move to state 0

    """
    def strategy1(self):
        #BTC SPREAD IS ~ .0002 * price
        print("")
        print("---"*10)
        print("Getting ticker info for {}".format(self.ticker))
        print(self.amountToBuy, self.amountToBuy)
        if self.amountToSell <= 0 and self.amountToBuy <= 0:
            self.end_condition_met = True
            return


        self.last_price, self.lowest_ask, self.highest_bid = self.get_ticker_info()
        trade_size = .00005
        margin = .0001
        # UPDATE BOT STATE

        if self.state == 0:
            print("Deciding to buy or sell next")
            if self.amountToBuy >= self.amountToSell:
                self.state = 1
            else:
                self.state = 3

        elif self.state == 1:
            print("Making buy order...")
            self.bid_order_price = self.last_price*(1 - margin)
            order_success =  self.maker_or_cancel_order("bid", self.bid_order_price, trade_size)
            if order_success == True:
                self.state = 2
                return
            elif order_success == "is_cancelled":
                print("order cancelled before execution - would have taken")
                return
            else:
                print("buy order failed")
                self.state = 5

        elif self.state == 2:
            print("Waiting for buy order to fill...")
            amount_remaining, original_amount = self.get_order_status()
            if amount_remaining == 0:
                self.amountToBuy -= original_amount
                self.state = 0
                return
            elif self.last_price > self.bid_order_price * (1 + 2*margin): #market has moved the other way
                "CANCEL THRESHOLD TRIGGERED"
                success = self.cancel_active_orders()
                if success:
                    self.amountToBuy -= (original_amount - amount_remaining) #amount bought
                    self.state = 0
                    return
                else:
                    print("cancel order failed")
                    self.state = 5


        elif self.state == 3:
            print("Making sell order")
            self.sell_order_price = self.last_price*(1 + margin)
            order_success = self.maker_or_cancel_order("ask", self.sell_order_price, trade_size)
            if order_success == True:
                self.state = 4
                return
            elif order_success == "is_cancelled":
                print("order cancelled before execution - would have taken")
                return
            else:
                print("sell order failed")
                self.state = 5

        elif self.state == 4:
            print("Waiting for sell to fill...")
            amount_remaining, original_amount = self.get_order_status()
            if amount_remaining == 0:
                self.amountToSell -= original_amount
                self.state = 0
                return
            elif self.last_price < self.sell_order_price * (1 - 2*margin):
                "CANCEL THRESHOLD TRIGGERED"
                success = self.cancel_active_orders()
                if success:
                    self.amountToSell -= (original_amount - amount_remaining) #amount successfully sold
                    self.state = 0
                    return
                else:
                    print("cancel order failed")
                    self.state = 5
        elif self.state == 5:
            pass #safe debugging state

    def update_server(self, url):
        print("updating server with order history...")
        requests.post(url, json = {
            "order_history" : self.order_history,
            "last_price" : self.last_price,
            "lowest_ask" : self.lowest_ask,
            "highest_bid" : self.highest_bid,
            "timestamp" :time.time()
            }
        )



    def run(self):
        iterations = 0
        while self.end_condition_met == False:
            sleep(1)
            self.strategy1()
            iterations += 1
            if (iterations % 5 == 0):
                #UPDATE SERVER
                self.update_server("http://localhost:8080")
        self.update_server("http://localhost:8080") #Final update


if __name__ == '__main__':
    g = GeminiBot("btcusd", .0005, .0005)
    g.run()
