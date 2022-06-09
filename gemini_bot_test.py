from gemini_bot import GeminiBot

ticker = "btcusd"
amountToBuy = .0005 #$15
amountToSell = .0005 #$15
g = GeminiBot(ticker, amountToBuy, amountToSell)
g.maker_or_cancel_order("bid", )
