

import sys
sys.path.insert(1, '/src/lib')


class TransactionWrapper:
    def __init__(self,_logger,_kite_login,_share_name = "SBIN",):
        

        self.kite_login = _kite_login
        
        self.logger = _logger
        self.transaction_buy = self.kite_login.kite.TRANSACTION_TYPE_BUY     
        self.transaction_sell = self.kite_login.kite.TRANSACTION_TYPE_SELL        
        self.share_name = _share_name
        self.stop_loss = None
        self.trigger_price = None
        self.variety = self.kite_login.kite.VARIETY_REGULAR
        self.product_type = self.kite_login.kite.PRODUCT_MIS       
        self.order_type = self.kite_login.kite.ORDER_TYPE_MARKET
       

        



    

    def buy_share_MIS(self,price,quantity):
    
        is_buy_status = False    
        order_id = self.kite_login.place_order("SBIN",quantity,price,self.transaction_buy,self.trigger_price,self.stop_loss,self.order_type,self.product_type,
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
                self.logging.error(e, exc_info=True)
                self.logging.error("Error waiting for order completion, loop will wait till order completion or failure...!!")
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

        return buy_status




                            
    
    def sell_share_MIS(self,price,quantity):
        is_sell_status = False  
        order_id = self.kite_login.place_order("SBIN",quantity,price,self.transaction_sell,self.trigger_price,self.stop_loss,self.order_type,self.product_type,
                                    self.product_type,self.variety)   
        print("order_id",order_id)
        if(order_id != 0):           
            is_sell_status = self.wait_for_transaction(order_id)        
        return is_sell_status

        
        





        