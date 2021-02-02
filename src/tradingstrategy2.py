from lib.kite_login_util import KiteLoginUtil
from tradingstrategypricecheck.tradingalgofollow2 import FollowAlgoSecond
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
        share_nse_name = "NSE:TATAMOTORS"
        # transactionWrapper = TransactionWrapper(logger,kite_login,"TATAMOTORS",kite_login.kite.PRODUCT_MIS)
        transactionWrapper = TransactionWrapper(logger,kite_login,"TATAMOTORS",kite_login.kite.PRODUCT_CNC)
        print("starting alog")
        logger.info('starting alog')
        algo = FollowAlgoSecond(kite_login,transactionWrapper,logger)       
        # purchase_diff = algo.find_purchase_diff("Tata Motors",url)
        purchase_diff = 20
        quantity = 40
        # share_nse_name = "NSE:SBIN"
        # purchase_diff = algo.find_purchase_diff("SBI",url)
        share_price = algo.get_share_price(share_nse_name)
        print("purchase_diff",purchase_diff)
        #print(type(share_price))    
        algo.tradealgostart(purchase_diff,share_nse_name,quantity)
        # algo.buy_share(275)
    except Exception as e:
        logger.error('Excetion occurred in the starting'+str(e))        
        print("Excetion occurred in the starting",str(e))

