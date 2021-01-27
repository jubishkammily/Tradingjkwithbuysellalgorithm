
from lib.kite_login_util import KiteLoginUtil

import logging


from tradingstrategypricecheck.transactionwrapper import TransactionWrapper


logger = logging.getLogger('my_logger')

if __name__ == "__main__":
    kite_login=KiteLoginUtil(exchange="NSE")
    kite_login.login()
    print(kite_login.kite.ltp(["NSE:SBIN"]))
    print(kite_login.ltp("NSE:NIFTY BANK"))

    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('tradezerodha.log')
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    print("starting alog")
    logger.info('starting alog')

    stop_loss = None
    trigger_price = None


    # order_id = kite_login.place_order("SBIN",1,275,kite_login.kite.TRANSACTION_TYPE_BUY,275,None,kite_login.kite.ORDER_TYPE_MARKET,kite_login.kite.VALIDITY_DAY,kite_login.kite.PRODUCT_CNC,kite_login.kite.VARIETY_REGULAR)
    # print("order_id",order_id)

    transactionWrapper = TransactionWrapper(logger,kite_login,"SBIN")
    transactionWrapper.buy_share_MIS(275.55,1)
     
    