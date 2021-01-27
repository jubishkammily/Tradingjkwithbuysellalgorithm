import os
import sys
import time
import base64
import requests
import keyring
from datetime import datetime
from smartapi import SmartConnect

from keyrings.alt.file import PlaintextKeyring
keyring.set_keyring(PlaintextKeyring())

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path.replace("src"+os.path.sep+"lib",""))

from src.lib.selenium_login_util import SeleniumUtil
from src.lib.colored_logging import CustomFormatter


#CRITICAL 50
#ERROR    40
#WARNING  30
#INFO     20
#DEBUG    10
#NOTSET   0



ts=datetime.now()
dt_time=ts.strftime("%d_%B_%Y")
dir_path = os.path.dirname(os.path.realpath(__file__))
instrument_file=dir_path+os.path.sep+"instrument_"+dt_time+".csv"
class KiteLoginUtil:

    def __init__(self,logging=None,exchange="NFO"):
        self.index=0
        if logging == None:
            self.logging=CustomFormatter().get_logger("kite_app",20)
        else:
            self.logging=logging

        self.exchange=exchange
        self.instrument_list={}
        self.read_credentials()

    def load_instruments(self):
        if os.path.exists(instrument_file):
            self.logging.debug("Instruments file exist")
        else:

            self.logging.debug("Reading Instruments:"+instrument_file)
            url="http://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
            try:
                headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
                           'content-type': 'application/json; charset=UTF-8'}

                response = requests.get(url, headers=headers, timeout=1000)
                if response.status_code == 200:
                    self.save_to_file(response.content)

            except Exception as e:
                self.logging.error(e)

    def save_to_file(self,response):
        with open(instrument_file, "w") as inst_file:
            inst_file.write(str(response))

    def read_credentials(self):
        self.logging.debug("Reading Credentials")
        try:
            self.username=self.decode(keyring.get_password("angel", "username"))
            self.password=self.decode(keyring.get_password("angel", "password"))
            self.api_key=keyring.get_password("angel", "api_key")
            self.api_secret=keyring.get_password("angel", "api_secret")
            self.profile=None
            self.load_instruments()
            self.logging.info('Completed Reading credentials from keys api_key {}'.format(self.api_key))
        except Exception as e:
            self.logging.critical('reading access token from file :')
            self.logging.critical(e, exc_info=True)

    def login(self,show=True):
        self.logging.debug("invoking generic login")
        try:
            self.kite = SmartConnect(api_key=self.api_key)
            self.logging.debug("setting access token")
            data = self.kite.generateSession(self.username,self.password)
            #refreshToken= data['data']['refreshToken']
            #feedToken=self.kite.getfeedToken()
            #self.profile=self.kite.getProfile(refreshToken)
            self.validate_lt_read()
            self.logging.debug("logged completed")
        except Exception as e:
            self.logging.warning("Failed to connect with existing session...\nTrying with fresh login, pls wait...!!")
            self.logging.warning("triggering selenium login due to failure:")
            self.logging.warning(e, exc_info=True)

    def save_access_token(self):
        self.logging.debug("invoking save_access_token")
        try:
            keyring.set_password("zerodha", "access_token",self.access_token)
            self.logging.debug("save_access_token completed")
        except Exception as e:
            self.logging.critical("Error saving new access_token to file, pls validate and manually save the same:"+str(self.access_token))
            self.logging.critical(e, exc_info=True)


    def validate_lt_read(self):
        ltprice=self.ltp("NSE", "SBIN-EQ", "3045")
        self.logging.info("Login Success validate SBIN-EQ with LTP is:"+str(ltprice))


    def write_instruments_to_file(self, instrument_file_path=str(dir_path)+"/instrument.csv"):
        self.logging.debug("invoking write_instruments_to_file")
        instrument_list = self.kite.instruments(exchange=self.exchange)
        with open(instrument_file_path, "w") as inst_file:
            heading="instrument_token,exchange_token,tradingsymbol,name,expiry,strike,tick_size,instrument_type,segment,exchange,last_price,lot_size"
            now = datetime.now()
            inst_file.write(heading+"\n")
            for instrument_dict  in instrument_list:
                data_line="instrument_token,exchange_token,tradingsymbol,name,expiry,strike,tick_size,instrument_type,segment,exchange,last_price,lot_size"
                for instrument_key  in instrument_dict:
                    if(instrument_key in data_line):
                        data_line=data_line.replace(str(instrument_key),str(instrument_dict[instrument_key]));
                    else:
                        data_line=data_line+","+str(instrument_key)
                inst_file.write(str(data_line)+"\n")
        self.logging.debug("completing write_instruments_to_file, generating html file")
        os.system("csvtotable "+instrument_file_path+" "+str(dir_path)+"/"+datetime.now().strftime("%Y%m%d_%H%M%S")+".html")
        self.logging.debug("Converted csv Successfully")

    def decode(self,base64_message):
        returnVal=None
        if(base64_message and len(base64_message)>0):
            base64_bytes = base64_message.encode('ascii')
            message_bytes = base64.b64decode(base64_bytes)
            returnVal= message_bytes.decode('ascii')
        return returnVal

    def encode(self,base64_message):
        returnVal=None
        if(base64_message and len(base64_message)>0):
            base64_bytes = base64_message.encode("ascii")
            message_bytes = base64.b64encode(base64_bytes)
            returnVal = message_bytes.decode("ascii")
        return returnVal

    def refresh_holdings(self):
        self.holdings_list=self.kite.holdings()
        #for holding in self.holdings_list:
        #    self.logging.debug(str(holding['tradingsymbol'])+"\n")

    def refresh_order(self):
        self.order_list=self.kite.holdings()
        #for order in self.order_list:
        #    print(str(order['tradingsymbol'])+"\n")

    def refresh_position(self):
        self.positions_list=self.kite.positions()
        #for net_position in self.positions_list["net"]:
        #    self.logging.debug(str(net_position['tradingsymbol']))

        #for day_position in self.positions_list["day"]:
        #    print(str(day_position['tradingsymbol']))

    def refresh_margin(self,segment="equity"):
        margin=self.kite.margins()
        return self.margin["equity"]["net"]


    def modify_order(self,order_id,transaction_type,tradingsymbol,quantity,price,trigger_price,stoploss):
        exchange=self.kite.EXCHANGE_NSE
        order_type=self.kite.ORDER_TYPE_LIMIT
        validity=self.kite.VALIDITY_DAY
        product=self.kite.PRODUCT_NRMLinstrument_file_path=str(dir_path)+"/instrument.csv"
        order_id=0
        try:
            order_id = self.kite.modify_order(tradingsymbol=tradingsymbol,
                                order_id=order_id,
                                exchange=exchange,
                                transaction_type=transaction_type,
                                quantity=quantity,
                                order_type=order_type,
                                price=price,
                                trigger_price=trigger_price,
                                stoploss=stoploss,
                                validity=validity,
                                product=product)
            self.logging.info("Sell Order placed for Share {} Qty {} Price {} ID is: {}".format(tradingsymbol,quantity,price,order_id))
        except Exception as e:
            self.logging.info("Sell Order placement for Share {} Qty {} Price {} failed:".format(tradingsymbol,quantity,price))
            self.logging.error(e, exc_info=True)
        return order_id


    def ltp(self,exchange,stock,code):
        price=""
        try:
            self.logging.debug("Reading price for stock")
            price=self.kite.ltpData(exchange,stock,code)['data']['ltp']
            self.logging.debug("Price for {} is {}".format(stock,price))
        except Exception as e:
            self.logging.error("Issue fetching ltp:")
            raise Exception("passing exception to parent",e)
        return price

    #def ltp(self,stock):
    #    price=""
    #    try:
    #        self.logging.debug("Reading price for stock")
    #        if(stock.startswith("NFO:BANKNIFTY")):
    #            search_stock_list=[stock]
    #            index_name="NSE:NIFTY BANK"
    #            search_stock_list.append(index_name)
    #            response=self.kite.ltp(search_stock_list)
    #            price=response[stock]['last_price']
    #            self.index=response[index_name]['last_price']
    #        else:
    #            price=self.kite.ltp([stock])[stock]['last_price']
    #            self.logging.debug("Price for {} is {}".format(stock,price))
    #    except Exception as e:
    #        self.logging.error("Issue fetching ltp:")
    #        raise Exception("passing exception to parent",e)
    #    return price

    #def ltp_old(self,stock):
    #    price=""
    #    try:
    #        self.logging.debug("Reading price for stock")
    #        price=self.kite.ltp([stock])[stock]['last_price']
    #        self.logging.debug("Price for {} is {}".format(stock,price))
    #    except Exception as e:
    #        self.logging.error("Issue fetching ltp:")
    #        raise Exception("passing exception to parent",e)
    #    return price


    def ltp_excep(self,stock):
        price=""
        while(True):
            try:
                self.logging.debug("Reading price for stock")
                price=self.kite.ltp([stock])[stock]['last_price']
                self.logging.debug("Price for {} is {}".format(stock,price))
                break
            except Exception as e:
                self.logging.critical("Issue fetching ltp, waiting 5 sec for network issue to get fixed...!!!")
                time.sleep(5)




        return price


    def place_order(self,tradingsymbol,quantity,price,transaction_type,trigger_price,stoploss,order_type,validity,product,variety):
        #exchange=self.kite.EXCHANGE_NSE,order_type=self.kite.ORDER_TYPE_LIMIT,validity=self.kite.VALIDITY_DAY,
        #product=self.kite.PRODUCT_NRML,transaction_type=self.kite.TRANSACTION_TYPE_BUY,variety=self.kite.VARIETY_REGULAR
        order_id=0
        orderparams = {
        "variety": "NORMAL",
        "tradingsymbol": "SBIN-EQ",
        "symboltoken": "3045",
        "transactiontype": "BUY",
        "exchange": "NSE",
        "ordertype": "LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": "19500",
        "squareoff": "0",
        "stoploss": "0",
        "quantity": "1"
        }
        try:
            order_id = self.kite.place_order(exchange=self.exchange,
                                    tradingsymbol=tradingsymbol,
                                    quantity=quantity,
                                    price=self.round_nearest(price),
                                    transaction_type=transaction_type,
                                    trigger_price=trigger_price,
                                    stoploss=stoploss,
                                    order_type=order_type,
                                    validity=validity,
                                    product=product,
                                    variety=variety)
            self.logging.info("Order placed for Share {} Qty {} Price {} ID is: {}".format(tradingsymbol,quantity,price,order_id))
        except Exception as e:
            self.logging.error("Error::Placing Order for Share {} Qty {} Price {} failed:".format(tradingsymbol,quantity,price))
            self.logging.error(e, exc_info=True)
        return order_id



    def get_orders(self):
        return self.kite.orders()

    def get_order(self,order_id):
        order_list=self.kite.orders()
        order_object=None
        for order in order_list:
            if(order["order_id"]==order_id):
                order_object=order
                break
        return order_object


    def get_order_status(self,id):
        order_list=self.kite.orders()
        order_status=None
        for order in order_list:
            if(order["order_id"]==id):
                order_status=order["status"]
                break
        return order_status

    def round_nearest(self,price, a=0.05):
        return round(round(price / a) * a,2)



if __name__ == "__main__":
    kite_login=KiteLoginUtil(exchange="NFO")
    kite_login.login()
    print(kite_login.ltp("NSE", "SBIN-EQ", "3045"))
    print(kite_login.ltp("NSE", "SBIN-EQ", "3045"))
    print(kite_login.ltp("NSE", "SBIN-EQ", "3045"))
    print(kite_login.ltp("NSE", "SBIN-EQ", "3045"))
    print(kite_login.ltp("NSE", "SBIN-EQ", "3045"))
    print(kite_login.ltp("NSE", "SBIN-EQ", "3045"))
    print(kite_login.ltp("NSE", "SBIN-EQ", "3045"))
    #print(kite_login.kite.ltp(["NSE:NIFTY BANK","NFO:BANKNIFTY20D1028000PE"]))
    #print(str(kite_login.ltp_new("NSE:SBIN")))
    #order_id=kite_login.place_order(tradingsymbol="INFY",quantity=1,price=1080.5,transaction_type="BUY",trigger_price=None,stoploss=None,order_type="LIMIT",validity="IOC",product="CNC",variety="regular")
    #print(order_id)
    #print(kite_login.get_orders())


    #tradingsymbol,quantity,price,trigger_price,stoploss,transaction_type,exchange,order_type,validity,product,transaction_type,product,variety
    #answer=input("Do you want to generate the csv file?")
    #if(answer=="Yes" or answer=="Y"):
    #    kite_login.write_instruments_to_file()


#    # Exchanges
#    EXCHANGE_NSE = "NSE"
#    EXCHANGE_BSE = "BSE"
#    EXCHANGE_NFO = "NFO"
#    EXCHANGE_CDS = "CDS"
#    EXCHANGE_BFO = "BFO"
#    EXCHANGE_MCX = "MCX"
#
#    # Constants
#    # Products
#    PRODUCT_MIS = "MIS"
#    PRODUCT_CNC = "CNC"
#    PRODUCT_NRML = "NRML"
#    PRODUCT_CO = "CO"
#    PRODUCT_BO = "BO"
#
#    # Order types
#    ORDER_TYPE_MARKET = "MARKET"
#    ORDER_TYPE_LIMIT = "LIMIT"
#    ORDER_TYPE_SLM = "SL-M"
#    ORDER_TYPE_SL = "SL"
#
#    # Varities
#    VARIETY_REGULAR = "regular"
#    VARIETY_BO = "bo"
#    VARIETY_CO = "co"
#    VARIETY_AMO = "amo"
#
#    # Transaction type
#    TRANSACTION_TYPE_BUY = "BUY"
#    TRANSACTION_TYPE_SELL = "SELL"
#
#    # Validity
#    VALIDITY_DAY = "DAY"
#    VALIDITY_IOC = "IOC"
