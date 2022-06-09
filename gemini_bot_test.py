from gemini_bot import GeminiBot
from time import sleep

ticker = "btcusd"
amountToBuy = .0003 #$15
amountToSell = .0003 #$15
g = GeminiBot(ticker, amountToBuy, amountToSell)


last_price, lowest_ask, highest_bid = g.get_ticker_info()
print("last price: {}, lowest ask: {}, highest bid: {}".format(last_price, lowest_ask, highest_bid))


# success = g.maker_or_cancel_order("ask", 60000, amountToBuy) # make an ask at 60000
# sleep(1)
# # success = g.maker_or_cancel_order("bid", 20, amountToBuy) # make an bid at 20
# # sleep(1)
# status = g.get_order_status()
# print(status)
# sleep(1)
# #
# print(g.order_history)
# g.cancel_active_orders()
# print(g.order_history)
# sleep(1)
# status = g.get_order_status()
