
import requests
import webbrowser
import re   # this is for regular expression
from bs4 import BeautifulSoup

from pprint import pprint
import pandas as pd 

import time
import threading

from databasemodel.databasemodelpricefollow import DatabaseModelPriceFollow



class FollowAlgo:
    def __init__(self,_kite_login,_trade_transact_wrapper,_logger,profit_add_amount):        
        self.kite_login = _kite_login
        self.logger = _logger
        self.list_row_buy = []
        self.list_row_sell = []
        self.fifty_paise = profit_add_amount
        self.trade_transact_wrapper = _trade_transact_wrapper
        self.quantity = 40
        

    def algorithm():        
        print ("This is determin_share_direction")


    # def find_section(self):
    #     print ("This is determin_share_direction")
    #     print(self.kite_login.kite.ltp(["NSE:SBIN"]))
    #     sharePriceObject = self.kite_login.kite.ltp(["NSE:SBIN"])
    #     for key in sharePriceObject:
    #         print(sharePriceObject[key]["last_price"])


    def get_share_price(self,share_name):
        share_price = 0  
        try:
            sharePriceObject = self.kite_login.kite.ltp([share_name])        
            share_price = sharePriceObject[share_name]["last_price"]
        except Exception as e:           
            print("Exception occurred get_share_price",str(e))
            share_price =0
        return share_price

    def get_most_active(self,share_name,url):
        resp = requests.get(url)
        html = resp.text
        soup = BeautifulSoup(html,"html.parser")
        table = soup.find(id="common-table")
        
        
        row =[]
        row_count = 0
        for tr in table.find_all('tr'):
            row = []
            #print(th.text.strip())
            if(row_count !=0):
                for td in tr.find_all('td'):
                    row.append(td.text.strip())
                if(row[0] == share_name):
                    return row
            row_count = row_count + 1
            
        
    
        return row


        
    def get_section(self,active_share):
        print("active_share",active_share)
        low = float(active_share[3])
        high = float(active_share[4])
        current = float(active_share[1])
    
        diff = high - low
        section = diff/20
        return section
    
    
    def find_purchase_diff(self,share_name,url):
        active_value = self.get_most_active(share_name,url)
        section = self.get_section(active_value)
        purchase_diff = section * 3
        print("find_purchase_diff")
        self.logger.info('find_purchase_diff')
        return purchase_diff

    def determine_bull(self,decision_time_in_seconds,total_index_times_time,price_change_count,share_name,market_result):
        share_price = self.get_share_price(share_name)
        current_price_First =  share_price
        print("Check for Bull market")
        # result = "None"
        max_time_forwhile=0
        index = 0
        print("Bull Index : ",index)
        self.logger.info("Bull Index : "+str(index))
        while True:        
             current_price_int = self.get_share_price(share_name)    
             # print("share_price",share_price)
             if(current_price_int > current_price_First):
                 current_price_First = current_price_int
                 index = index + 1
                 print("Bull Index : ",index)
                 self.logger.info("Bull Index : "+str(index))
                 if index == price_change_count:
                     market_result.result = "Bull"
                     break                       
             if(max_time_forwhile == total_index_times_time):
                 print("No change in direction Bull Check for 180 seconds")
                 self.logger.info("No change in direction Bull Check for 180 seconds")
                 market_result.result = "None"
                 break            
             time.sleep(decision_time_in_seconds)
             max_time_forwhile = max_time_forwhile + 1 
             if(market_result.result is not "None"):
                 break      
        print("determine_bull",market_result.result)
        # return result
    
    def determine_bear(self,decision_time_in_seconds,total_index_times_time,price_change_count,share_name,market_result):
        share_price = self.get_share_price(share_name)
        current_price_First =  share_price
        print("Check for Bear market")
        # result = "None"
        max_time_forwhile=0  
        index = 0      
        print("Bear Index : ",index)
        self.logger.info("Bear Index : "+str(index))
        while True:        
            current_price_int = self.get_share_price(share_name)                    
            # print("share_price",share_price)
            if(current_price_int < current_price_First):
                current_price_First = current_price_int
                index = index + 1
                print("Bear Index : ",index)
                self.logger.info("Bear Index : "+str(index))
                if index == price_change_count:
                    market_result.result = "Bear"
                    break                                       
            if(max_time_forwhile == total_index_times_time):
                print("No change in direction Bear Check for 180 seconds")
                self.logger.info("No change in direction Bear Check for 180 seconds")
                market_result.result = "None"
                break   
            time.sleep(decision_time_in_seconds)
            max_time_forwhile = max_time_forwhile + 1
            if(market_result.result is not "None"):
                break

        print("determine_bear",market_result.result)    
        # return result

    
    
    def determin_share_direction(self,share_name):

        market_result = MarketResult()
        
        share_price = self.get_share_price(share_name)
        current_price_First =  share_price
        print("current_price_First :",current_price_First)
        self.logger.info("current_price_First : "+ str(current_price_First))
        index = 0
        result = "None"
        # each decision_time_in_seconds for 180 times the seconds here it will be 15 mins max
        decision_time_in_seconds = 5 
        # total_index_times_time = 180
        total_index_times_time = 60
        max_time_forwhile = 0
        price_change_count = 7

        bull_thread = threading.Thread(target=self.determine_bull,args=(decision_time_in_seconds,total_index_times_time,price_change_count,share_name,market_result),daemon=True)
        bear_thread = threading.Thread(target=self.determine_bear,args=(decision_time_in_seconds,total_index_times_time,price_change_count,share_name,market_result),daemon=True)

        bull_thread.start()
        bear_thread.start()

        bull_thread.join()
        bear_thread.join()
    
        # while result == "None":
        #     if(result == "None"):
        #         result = self.determine_bear(decision_time_in_seconds,total_index_times_time,price_change_count,share_name,market_result)
            
        #     if(result == "None"):
        #         result = self.determine_bull(decision_time_in_seconds,total_index_times_time,price_change_count,share_name,market_result)
    
        print("market_result.result  :",market_result.result)
        self.logger.info("market_result.result  :"+market_result.result)
        result = market_result.result
        return result
    

    def buy_share(self,current,quantity): 
        try:
            # is_buy_status = self.trade_transact_wrapper.buy_share_MIS(current,quantity)        
            is_buy_status = True       
            if(is_buy_status):
                print("Bought "+str(quantity)+" shares for rs :",current)
                self.logger.info("Bought "+str(quantity)+"  shares for rs : "+ str(current))
            else:
                print("BUY Failed")
                self.logger.info("BUY Failed")  
        except Exception as e:
            self.logger.error('Excetion occurred buy_share '+str(e))                
            print("Exception occurred in buy_share ",str(e))     

        return is_buy_status



    def sell_share(self,current,quantity):   
        try:
            # is_sell_status = self.trade_transact_wrapper.sell_share_MIS(current,quantity)
            is_sell_status = True   
            if(is_sell_status):
                print("Sold "+str(quantity)+"  shares for rs :",current)
                self.logger.info("Bought "+str(quantity)+"  shares for rs : "+ str(current))
            else:
                print("SELL Failed")
                self.logger.info("SELL Failed")     
        except Exception as e:
            self.logger.error('Excetion occurred sell_share '+str(e))                
            print("Exception occurred in sell_share ",str(e))        
        return is_sell_status
    
    def track_buy(self,bought_price,stop_loss,purchase_diff,share_name,quantity):    
        current_price_First = self.get_share_price(share_name)            
        is_sold = False

        test_profit_fifty_paise = bought_price + self.fifty_paise


        while True:          
            current_price_int = self.get_share_price(share_name)     
            if(current_price_int!=0):                 
                stop_loss_2 = current_price_int - purchase_diff
                if(stop_loss_2 > stop_loss):
                    stop_loss = stop_loss_2
                    print("Updated stop_loss for track buy: ",stop_loss)
                    print("Current Shre Price  : ",current_price_int)
                    self.logger.info("Updated stop_loss for track buy: "+ str(stop_loss))
                    self.logger.info("Current Shre Price  : " + str(current_price_int))
                if(current_price_int < stop_loss):
                    if(current_price_int!=0):
                        is_sold = self.sell_share(current_price_int,quantity)
                        self.logger.info("Loss sell with 50 paise")
                        print("Loss sell with 50 paise")
                elif(current_price_int > test_profit_fifty_paise):
                    is_sold = self.sell_share(current_price_int,quantity)
                    self.logger.info("Booked sell with 50 paise")
                    print("Booked sell with 50 paise")
                            
     
                if(is_sold):
                    self.list_row_buy[5] = current_price_int
                    self.list_row_buy[4] = "Sold"
                    self.test_table.save_current_transaction(self.list_row_buy)
                    self.test_table.add_row_to_existing_table(self.list_row_buy)
                    break

            time.sleep(2)

        return is_sold
    
    def track_sell(self,sold_price,stop_loss,purchase_diff,share_name,quantity):
        current_price_First = self.get_share_price(share_name)  
        is_bought = False

        test_profit_fifty_paise = sold_price - self.fifty_paise


        while True:
            current_price_int = self.get_share_price(share_name)
            if(current_price_int!=0):
                stop_loss_2 = current_price_int + purchase_diff
                if(stop_loss_2 < stop_loss):
                    stop_loss = stop_loss_2
                    print("Updated stop_loss for track sell: ",stop_loss)
                    print("Current Shre Price  : ",current_price_int)
                    self.logger.info("Updated stop_loss for track sell: "+ str(stop_loss))
                    self.logger.info("Current Shre Price  : " + str(current_price_int))
                if(current_price_int > stop_loss):
                    if(current_price_int!=0):
                        is_bought = self.buy_share(current_price_int,quantity)
                        self.logger.info("Loss buy with 50 paise")
                        print("Loss buy with 50 paise")
                elif(current_price_int < test_profit_fifty_paise):
                    is_bought = self.buy_share(current_price_int,quantity)
                    self.logger.info("Booked buy with 50 paise")
                    print("Booked buy with 50 paise")

                if(is_bought):
                    self.list_row_sell[5] = current_price_int
                    self.list_row_sell[4] = "Bought"
                    self.test_table.save_current_transaction(self.list_row_sell)
                    self.test_table.add_row_to_existing_table(self.list_row_sell)
                    break

            time.sleep(2)
    
        return is_bought
    
    def tradealgostart(self,purchase_diff,share_name,quantity):

        self.test_table = DatabaseModelPriceFollow()

        while True:
            self.logger.info('starting algorithm')
            print ("This is determin_share_direction")
            self.logger.info('This is determin_share_direction')
            result = self.determin_share_direction(share_name)
            print("result : ",result)
            current_price_int = self.get_share_price(share_name)            
            bought_price = 0
            print ("This is Normal Buying and selling ")
            self.logger.info('This is Normal Buying and selling')

            if(result == "Bull"):  
                print ("This is buying ")
                self.logger.info('This is buying')

                buy_status = self.buy_share(current_price_int,quantity)                
                bought_price = current_price_int
                stop_loss = bought_price - purchase_diff
                if(buy_status):                    
                    self.list_row_buy = [share_name,"Bought",current_price_int,stop_loss,"None",0]
                    self.test_table.save_current_transaction(self.list_row_buy)
                    print("stop_loss set after buy :", str(stop_loss))
                    self.logger.info('stop_loss set after buy : '+ str(stop_loss))
                    self.track_buy(bought_price,stop_loss,purchase_diff,share_name,quantity)
                time.sleep(10)


                
    
            if(result == "Bear"):
                print ("This is shorting ")
                self.logger.info('This is shorting')
                
                sell_status = self.sell_share(current_price_int,quantity)
                sold_price = current_price_int
                stop_loss = sold_price + purchase_diff
                if(sell_status):                    
                    self.list_row_sell = [share_name,"Sold",current_price_int,stop_loss,"None",0]
                    self.test_table.save_current_transaction(self.list_row_sell)
                    print("stop_loss set after Sell :", str(stop_loss))
                    self.logger.info('stop_loss set after Sell : '+ str(stop_loss))
                    self.track_sell(sold_price,stop_loss,purchase_diff,share_name,quantity)
                time.sleep(10)

            time.sleep(10)




class MarketResult:
    result = "None"

