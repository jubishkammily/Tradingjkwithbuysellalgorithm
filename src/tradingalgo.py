from lib.kite_login_util import KiteLoginUtil
from tradingstrategypricecheck.tradingalgopffollow import FollowAlgo
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

    transactionWrapper = TransactionWrapper(logger,kite_login,"SBIN")

    print("starting alog")
    logger.info('starting alog')
    algo = FollowAlgo(kite_login,transactionWrapper,logger)


    

    url = "https://www.ndtv.com/business/marketdata/most-active-stocks-by-volume/allnse_daily"
    share_nse_name = "NSE:SBIN"
    purchase_diff = algo.find_purchase_diff("SBI",url)
    share_price = algo.get_share_price(share_nse_name)
    print("purchase_diff",purchase_diff)
    
    #print(type(share_price))
    # algo.tradealgostart(purchase_diff,share_nse_name)
    algo.buy_share(275)

