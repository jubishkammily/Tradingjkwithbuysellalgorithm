import requests
import webbrowser
import re   # this is for regular expression
from bs4 import BeautifulSoup

from pprint import pprint
import pandas as pd 

import time

from databasemodel.databasemodelpricefollow import DatabaseModelPriceFollow



class LongTermTradeStrategy :
    def __init__(self,_kite_login,_trade_transact_wrapper,_logger):        
        self.kite_login = _kite_login
        self.logger = _logger
        self.list_row_buy = []
        self.list_row_sell = []
        self.fifty_paise = 0.50
        self.trade_transact_wrapper = _trade_transact_wrapper
        self.quantity = 20
    
    def trade_long_algo_start_buy(self,share_name,buy_price,quantity):

        is_bought = False
        current_price= self.trade_transact_wrapper.get_share_price_generic(share_name)
        print("current_price",current_price)

        while True:
            if(current_price == buy_price):
                self.trade_transact_wrapper.buy_share_generic(current_price,quantity)
                is_bought = True   
                time.sleep(5)             
                break
        

        if(is_bought):
            self.strategy_sell_stoploss_after_profit(share_name,bought_price,quantity)



        

            
        
        return isFinished
        




    def strategy_sell_stoploss_after_profit(self,share_name,bought_price,quantity):

        stop_loss = 0
        profit_price = bought_price + 1
        add_amount = 0.50
        profit_price_plus = profit_price + add_amount
        is_sell_success = False

        while True:
            current_price= self.trade_transact_wrapper.get_share_price_generic(share_name)

            if(current_price >= profit_price_plus):                      
                stop_loss == profit_price
            
            if(stop_loss!=0):
                stop_loss2 = current_price - add_amount
                if(stop_loss2 >stop_loss):
                    stop_loss == stop_loss2
                    print("updated stoploss price",str(stop_loss))
                    self.logger.error("updated stoploss price",str(stop_loss))    
                if(current_price < stop_loss):
                    is_sell_success = self.trade_transact_wrapper.sell_share_generic(current_price,quantity)
                    break



    def find_buy_price(high,low):
        avg = (high + low) / 2

        two_percent = (2 * avg) /100   

        range_low = avg - two_percent
        range_high  = avg  + two_percent





           


        





    


    


