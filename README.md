# Features In-Progress

- Reading stoploss and trailing margin from the candle chart and populating to trend DB every 1 minute, this will run within the trend analyzer server
     > New trading class using stoploss and trailing margin from above implementation

- Candle Chart analysis single chart bullish and bearish patterns (Initially Marubozu,Hammer,Spinning Top, Doji) for Auto trading with trend and loop feature.
     > New Auto trading class using trend from above implementation

- Reading Position before BuyAndSell and SellAndBuy to find if already bought or sold and perform the second action if already bought or sold  
- Paper trade testing on the above features using new server
- Opponent stoploss-hit feature for dual trading, planning to implement using position reading every 30 minute
