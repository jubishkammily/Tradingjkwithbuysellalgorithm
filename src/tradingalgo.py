from lib.kite_login_util import KiteLoginUtil
from tradingstrategypricecheck.tradingalgopffollow import FollowAlgo
from tradingstrategypricecheck.tradingalgopffollowstrategy2 import FollowAlgo2
from tradingstrategypricecheck.transactionwrapper import TransactionWrapper

import logging

logger = logging.getLogger('my_logger')

if __name__ == "__main__":
    
    kite_login=KiteLoginUtil(exchange="NSE")
    kite_login.login()
    print(kite_login.kite.ltp(["NSE:NIFTY BANK"])) 
    print(kite_login.ltp("NSE:NIFTY BANK"))
    
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('tradezerodha.log')
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    


    

    url = "https://www.ndtv.com/business/marketdata/most-active-stocks-by-volume/allnse_daily"

    try:
        # share_nse_name = "NSE:TATAMOTORS"
        # share_name_t = "TATAMOTORS"
        # share_nse_name = "NSE:ICICIBANK"
        # share_name_t = "ICICIBANK"
        share_nse_name = "NSE:SBIN"
        share_name_t = "SBIN"
        # transactionWrapper = TransactionWrapper(logger,kite_login,"TATAMOTORS",kite_login.kite.PRODUCT_MIS)
        transactionWrapper = TransactionWrapper(logger,kite_login,kite_login.kite.PRODUCT_MIS,share_name_t)
        print("starting alog")
        logger.info('starting alog')
        # profit_add_amount = 0.50
        profit_add_amount = 0.50
        # algo = FollowAlgo(kite_login,transactionWrapper,logger,profit_add_amount)       
        algo = FollowAlgo2(kite_login,transactionWrapper,logger,profit_add_amount)       
        # purchase_diff = algo.find_purchase_diff("Tata Motors",url)
        purchase_diff = 6
        quantity = 300
        
        # purchase_diff = algo.find_purchase_diff("SBI",url)
        share_price = algo.get_share_price(share_nse_name)
        print("Test share Price"+share_nse_name+" ",share_price)    
        print("purchase_diff",purchase_diff)
        
        algo.tradealgostart(purchase_diff,share_nse_name,quantity)
        # algo.buy_share(275)
    except Exception as e:
        logger.error('Excetion occurred in the starting'+str(e))        
        print("Excetion occurred in the starting",str(e))

