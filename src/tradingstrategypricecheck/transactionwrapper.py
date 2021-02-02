
import requests
import webbrowser
import re   # this is for regular expression
from bs4 import BeautifulSoup

from pprint import pprint
import pandas as pd 

import time

from databasemodel.databasemodelpricefollow import DatabaseModelPriceFollow


import sys
sys.path.insert(1, '/src/lib')


class TransactionWrapper:
    def __init__(self,_logger,_kite_login,_product_type,_share_name = "SBIN"):
        

        self.kite_login = _kite_login

        
        self.logger = _logger
        self.transaction_buy = self.kite_login.kite.TRANSACTION_TYPE_BUY     
        self.transaction_sell = self.kite_login.kite.TRANSACTION_TYPE_SELL        
        self.share_name = _share_name
        self.stop_loss = None
        self.trigger_price = None
        self.variety = self.kite_login.kite.VARIETY_REGULAR
        self.product_type = _product_type       
        self.order_type = self.kite_login.kite.ORDER_TYPE_MARKET
        self.validity = self.kite_login.kite.VALIDITY_DAY
       


    


    def set(product_type):
        if(product_type == "CNC"):
            self.product_type =  self.kite_login.kite.PRODUCT_CNC
        elif(product_type=='MIS'):
            self.product_type =  self.kite_login.kite.PRODUCT_MIS
    

    def buy_share_generic(self,current,quantity): 
        try:
            is_buy_status = self.buy_share_MIS(current,quantity)        
            if(is_buy_status):
                print("Bought "+str(quantity)+" shares for rs :",current)
                self.logger.info("Bought "+str(quantity)+" shares for rs : "+ str(current))
            else:
                print("BUY Failed")
                self.logger.info("BUY Failed")  
        except Exception as e:
            self.logger.error('Excetion occurred buy_share '+str(e))                
            print("Exception occurred in buy_share ",str(e))     

        return is_buy_status
    

    
    def sell_share_generic(self,current,quantity):   
        try:
            is_sell_status = self.sell_share_MIS(current,quantity)
            if(is_sell_status):
                print("Sold "+str(quantity)+" shares for rs :",current)
                self.logger.info("Bought "+str(quantity)+" shares for rs : "+ str(current))
            else:
                print("SELL Failed")
                self.logger.info("SELL Failed")     
        except Exception as e:
            self.logger.error('Excetion occurred sell_share '+str(e))                
            print("Exception occurred in sell_share ",str(e))        
        return is_sell_status
    

    
    def get_share_price_generic(self,share_name):
        share_price = 0  
        try:
            sharePriceObject = self.kite_login.kite.ltp([share_name])        
            share_price = sharePriceObject[share_name]["last_price"]
        except Exception as e:           
            print("Exception occurred get_share_price",str(e))
        return share_price


    
    def get_most_active_generic(self,share_name,url):
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

       

        



    

    def buy_share_MIS(self,price,quantity):
    
        is_buy_status = False    
        order_id = self.kite_login.place_order(self.share_name,quantity,price,self.transaction_buy,self.trigger_price,self.stop_loss,self.order_type,self.validity,
                                    self.product_type,self.variety)                                       
        print("order_id",order_id)
        if(order_id != 0):         
            is_buy_status = self.wait_for_transaction(order_id)        
        return is_buy_status
            

    



    def wait_for_transaction(self,order_id):
        order_object=None
        buy_status_success = True
        while True:
            try:
                order_object=self.kite_login.get_order(order_id)
            except Exception as e:                
                self.logger.error("Error waiting for order completion, loop will wait till order completion or failure...!!")
                time.sleep(0.5)
            if order_object != None:
                status=order_object["status"]
                price=order_object["average_price"]
                if(status=="COMPLETE"):
                    buy_status_success = True
                    break
                if(status=="CANCELLED" or status=="REJECTED"):
                    buy_status_success = False
                    break

        return buy_status_success




                            
    
    def sell_share_MIS(self,price,quantity):
        is_sell_status = False  
        order_id = self.kite_login.place_order(self.share_name,quantity,price,self.transaction_sell,self.trigger_price,self.stop_loss,self.order_type,self.validity,
                                    self.product_type,self.variety)   
        print("order_id",order_id)
        if(order_id != 0):           
            is_sell_status = self.wait_for_transaction(order_id)        
        return is_sell_status

        
        





        