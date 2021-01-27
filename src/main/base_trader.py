#!/usr/bin/python
import os
import sys
import time
import keyring
import _thread
import threading
import numpy
from datetime import datetime


dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path.replace("src"+os.path.sep+"main",""))

pl_file_name="pl_file"+datetime.now().strftime("_%Y_%b_%d")+".csv"
profit_log_path=dir_path.replace("src"+os.path.sep+"main","statement"+os.path.sep+pl_file_name)
bs_file_name="bs_file"+datetime.now().strftime("_%Y_%b_%d")+".csv"
buy_and_sell_log_path=dir_path.replace("src"+os.path.sep+"main","statement"+os.path.sep+bs_file_name)
from src.lib.colored_logging import CustomFormatter
from src.lib.kite_login_util import KiteLoginUtil
from src.lib.read_break_even import BrokerageReader

class FixedList(list):
 def append(self, item):
     list.append(self, item)
     if len(self) > 2150: del self[0]

class BaseTrader:

    ######################################
    ### Unit Test Implimented - 100%
    ######################################
    def __init__(self,stock,quantity,validity,product,variety,exchange,type,sl_margin_percentage,traling_margin_percentage,loop=1,delay=2,consider_positions=True):
        self.loop=loop
        self.stock_log_name="{}_{}".format(stock,exchange)
        self.logging=CustomFormatter(name=self.stock_log_name).get_logger(stock,20)
        self.delay=delay
        self.stock=stock
        self.quantity=quantity
        self.exchange=exchange
        self.type=type
        self.sl_margin_percentage=sl_margin_percentage
        self.traling_margin_percentage=traling_margin_percentage
        self.running=True
        self.buy_flag=False
        self.sell_flag=False
        self.validity=validity
        self.product=product
        self.variety=variety
        self.lt_price_list=FixedList()
        self.minimum_buy_margin=0
        self.minimum_sell_margin=0
        self.stoploss_hit_flag=False
        self.open=0
        self.close=0
        self.high=0
        self.low=0
        self.mean=0
        self.counter=0
        self.breakeven=0
        self.trend_analysis=""
        self.buy_trend=""
        self.sell_trend=""
        self.consider_positions=consider_positions
        self.logging.critical("\n\nTracking \nstock::{} \nexchange::{} \nquantity::{} \ntype::{} \nsl_margin_percentage::{} \ntraling_margin_percentage::{} \nvalidity::{} \nproduct::{}  \nvariety::{} \n\n\nloop::{} \n\n".format(stock,exchange,quantity,type,sl_margin_percentage,traling_margin_percentage,validity,product,variety,loop))


    # cannot test this, can have seperate test for kite_login
    def kite_init(self):
        self.logging.debug("Starting Kite Login")
        self.kite_login=KiteLoginUtil(exchange=self.exchange,logging=self.logging)
        self.kite_login.login()
        self.logging.debug("Kite Login Completed")

    # Unit Test implemented seperately for each functions
    def init_kite_and_price_pointers(self):
        ltprice=self.kite_login.ltp(str(self.exchange)+":"+str(self.stock))
        self.init_price_pointers_buy(ltprice)
        self.init_price_pointers_sell(ltprice)
        self.init_breakeven(ltprice)
        self.init_margin_price_pointers(ltprice)


    def validate_stock_in_position_or_holdings(self):
        self.kite_login.refresh_position()
        for position in self.kite_login.positions_list["net"]:
            if position['tradingsymbol']==self.stock:
                if self.type=="SellAndBuy":
                    if(position['quantity']==(-1*self.quantity)):
                        self.logging.critical("Stock Already Exist in Sell position, using the same...!!!")
                        self.sl_price_sell=position['average_price']
                        self.update_loop_indicators("SellCompleted")
                        self.set_indicators_after_sell()
                        new_sl=position['last_price']+self.sl_margin_percentage
                        #if self.sl_price_buy<new_sl:
                        self.sl_price_buy=new_sl

                elif self.type=="BuyAndSell":
                    if(position['quantity']==(self.quantity)):
                        self.logging.critical("Stock Already Exist in Buy position, using the same...!!!")
                        self.sl_price_buy=position['average_price']
                        self.update_loop_indicators("BuyCompleted")
                        self.set_indicators_after_buy()
                        new_sl=position['last_price']-self.sl_margin_percentage
                        #if self.sl_price_sell>new_sl:
                        self.sl_price_sell=new_sl


    # Unit Test PENDING
    def init_breakeven(self,ltprice):
        self.breakeven=1

        type=""
        if(self.exchange == "NSE"):
            type="intraday"
        elif(self.exchange == "MCX"):
            type="commodity"
        elif(self.exchange == "NFO"):
            type="option"

        try:
            if(len(type)==0):
                raise Exception()
            breakeven_obj=BrokerageReader(ltprice,self.quantity,self.logging,type=type)
            self.breakeven=breakeven_obj.get_breakeven()
            self.breakeven+=self.breakeven*15/100
        except Exception as e:
            self.logging.error("Error in breakeven value calculation....!!!")
            self.logging.error(e, exc_info=True)

    # no need to be tested
    def start_price_monitoring_thread(self):
        self.set_loop_indicators()
        if(self.consider_positions=='True'):
            self.validate_stock_in_position_or_holdings()
        self.logging.debug("Starting Thread................!!!")
        _thread.start_new_thread(self.price_checker,("PriceMonitorThread",self.delay,self.stock))
        self.logging.debug("Thread is up................!!!")


    # Unit Test Pending Validation
    def price_checker(self,threadName,delay,stock):
        try:
            while (self.buy_flag or self.sell_flag):
                ltp=""
                while (True):
                    try:
                        ltp=self.kite_login.ltp(str(self.exchange)+":"+str(self.stock))
                        break
                    except Exception as e:
                        self.logging.critical("Issue fetching ltp, waiting 5 sec for network issue to get fixed...!!!")
                        time.sleep(5)

                self.set_price(ltp)
                self.update_trend_analysis(ltp)
                self.logging.debug("Looping in price_checker::ltprice::{}".format(ltp))
                self.show_variables(ltp)
                self.price_action(ltp)
                time.sleep(delay)

            self.start_next_iteration()
        except Exception as e:
            self.logging.error("Error in looping thread, exiting....!!!")
            self.logging.error(e, exc_info=True)
        self.running=False


    # Unit Test PENDING
    def update_trend_analysis(self,ltp):
        if(len(self.lt_price_list)>5):
            self.mean=numpy.mean(self.lt_price_list)
            self.open=self.lt_price_list[0]
            self.close=self.lt_price_list[len(self.lt_price_list)-1]
            self.high=max(self.lt_price_list)
            self.low=min(self.lt_price_list)
        self.lt_price_list.append(ltp)
        self.profit=-1

        if self.sell_flag and self.type=="BuyAndSell":
        	profit_margin=ltp-self.sl_price_buy
        	self.profit=(profit_margin-self.breakeven)*self.quantity

        if self.buy_flag and self.type=="SellAndBuy":
        	profit_margin=self.sl_price_sell-ltp
        	self.profit=(profit_margin-self.breakeven)*self.quantity



    ######################################
    ### Unit Test Implimented - 100%
    ######################################
    def set_loop_indicators(self):
        if(self.type == "BuyAndSell" or self.type == "Buy"):
            self.buy_flag=True
            self.sell_flag=False
        elif(self.type == "SellAndBuy" or self.type == "Sell"):
            self.buy_flag=False
            self.sell_flag=True



    ######################################
    ### Unit Test Implimented - 100%
    ######################################
    def need_new_file(self,path):
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return False
        else:
            return True

    # Unit Test PENDING
    def update_buy_and_sell_to_file(self,action):
        price=""
        trend=""
        heading=""

        ts=datetime.now()
        dt_time=ts.strftime("%d-%B-%Y_%H:%M:%S")

        if(action=="Buy"):
            price=self.sl_price_buy
            trend=self.trend_analysis
        elif(action=="Sell"):
            price=self.sl_price_sell
            trend=self.trend_analysis

        if self.need_new_file(buy_and_sell_log_path):
            heading="STOCK\tQUANTITY\tSTRATAGY\tACTION\tPRICE\tBROKERAGE\tTREND\tTIME\n"
        try:
            with open(buy_and_sell_log_path, "a+") as file:
                if(len(heading)>0):
                    file.write(heading)
                file.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(self.stock,self.quantity,self.type,action,price,round(self.breakeven,2),trend,dt_time))
        except Exception as e:
            self.logging.error("Error updating buy & sell statement, process will continue....!!!")
            self.logging.error(e, exc_info=True)

    # Unit Test PENDING
    def update_profit_to_file(self):
        heading=""
        ts=datetime.now()
        dt_time=ts.strftime("%d-%B-%Y_%H:%M:%S")
        if self.need_new_file(profit_log_path):
            heading="STOCK\tQUANTITY\tSTRATAGY\tBROKERAGE\tBUY\tB_TREND\tSELL\tS_TREND\tMARGIN\tNET_PROFIT\tITERATION\tTIME\n"
        try:
            with open(profit_log_path, "a+") as file:
                if(len(heading)>0):
                    file.write(heading)
                file.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(self.stock,self.quantity,self.type,round(self.breakeven,2),self.sl_price_buy,self.buy_trend,self.sl_price_sell,self.sell_trend,self.profit_margin,self.net_profit,self.counter,dt_time))
        except Exception as e:
            self.logging.error("Error updating p&l statement, process will continue....!!!")
            self.logging.error(e, exc_info=True)

    ######################################
    ### Unit Test Implimented - 100%
    ######################################
    def show_profit_margine_from_sell(self):
        #self.profit_margin=round(self.sl_price_sell-self.sl_price_buy,2)
        self.profit_margin=round((self.sl_price_sell-self.sl_price_buy)-self.breakeven,2)
        self.net_profit=round(self.profit_margin*self.quantity,2)
        profile_line="{}::stock {} breakeven:{} buy price:{}-{} sell price:{}-{} profit margin:{} net profit:\t{}\tin {} iterations".format(self.type,self.stock,round(self.breakeven,2),self.sl_price_buy,self.buy_trend,self.sl_price_sell,self.sell_trend,self.profit_margin,self.net_profit,self.counter)
        self.logging.info(profile_line)
        #self.update_profit_to_file(profile_line)
        self.update_profit_to_file()

    ######################################
    ### Unit Test Implimented - 100%
    ######################################
    def show_profit_margine_from_buy(self):
        #self.profit_margin=round(self.sl_price_sell-self.sl_price_buy,2)
        self.profit_margin=round(self.sl_price_sell-self.sl_price_buy-self.breakeven,2)
        self.net_profit=round(self.profit_margin*self.quantity,2)
        profit_line="{}::stock {} breakeven:{} buy price:{}-{} sell price:{}-{} profit margin:{} net profit:\t{}\tin {} iterations".format(self.type,self.stock,round(self.breakeven,2),self.sl_price_buy,self.buy_trend,self.sl_price_sell,self.sell_trend,self.profit_margin,self.net_profit,self.counter)
        #self.logging.info(profit_line)
        self.update_profit_to_file()

    ######################################
    ### Unit Test Implimented - 100%
    ######################################
    def update_loop_indicators(self,action):
        if(action == "BuyCompleted" and self.type == "BuyAndSell"):
            self.buy_flag=False
            self.sell_flag=True
        elif(action == "SellCompleted" and self.type == "SellAndBuy"):
            self.buy_flag=True
            self.sell_flag=False
        else:
            self.buy_flag=False
            self.sell_flag=False
        if(action == "SellCompleted" and self.type == "BuyAndSell" or self.type == "Sell"):
                self.sell_trend=self.trend_analysis
                self.show_profit_margine_from_sell()
        elif(action == "BuyCompleted" and self.type == "SellAndBuy" or self.type == "Buy"):
                self.buy_trend=self.trend_analysis
                self.show_profit_margine_from_buy()

    ######################################
    ### Unit Test Implimented - 100%
    ######################################
    def wait_for_order_completion_buy(self,order_id):
        while(True):
            order_object=None
            try:
                order_object=self.kite_login.get_order(order_id)
            except Exception as e:
                self.logging.error(e, exc_info=True)
                self.logging.error("Error waiting for order completion, loop will wait till order completion or failure...!!")
                time.sleep(0.5)
            if order_object != None:
                status=order_object["status"]
                price=order_object["average_price"]
                if(status=="OPEN" or status=="VALIDATION PENDING" or status=="PENDING"):
                    self.logging.warning("order {} is still pending, program will wait till complete execution".format(order_id))
                elif(status=="CANCELLED" or status=="REJECTED"):
                    self.logging.critical("order {} is cancelled, program will exit as error...!!!".format(order_id))
                    raise Exception()
                elif(status=="COMPLETE"):
                    self.sl_price_buy=price
                    self.logging.info("order {} is successfull".format(order_id))
                    break;
                else:
                    self.logging.info("order {} is in unknown status::{}, loop will continue...!!!".format(order_id,status))
            else:
                self.logging.critical("order {} is in None, loop will continue...!!!")


    ######################################
    ### Unit Test Implimented - 100%
    ######################################
    def wait_for_order_completion_sell(self,order_id):
        while(True):
            order_object=None
            try:
                order_object=self.kite_login.get_order(order_id)
            except Exception as e:
                self.logging.error(e, exc_info=True)
                self.logging.error("Error waiting for order completion, loop will wait till order completion or failure...!!")
                time.sleep(0.5)
            if order_object != None:
                status=order_object["status"]
                price=order_object["average_price"]
                if(status=="OPEN" or status=="VALIDATION PENDING" or status=="PENDING"):
                    self.logging.warning("order {} is still pending, program will wait till complete execution".format(order_id))
                elif(status=="CANCELLED" or status=="REJECTED"):
                    self.logging.critical("order {} is cancelled, program will exit as error...!!!".format(order_id))
                    raise Exception()
                elif(status=="COMPLETE"):
                    self.sl_price_sell=price
                    self.logging.info("order {} is successfull".format(order_id))
                    break;
                else:
                    self.logging.info("order {} is in unknown status::{}, loop will continue...!!!".format(order_id,status))
            else:
                self.logging.critical("order is None, loop will continue...!!!")



    ######################################
    ### Unit Test Implimented - 100%
    ######################################
    def reset_variables(self):
        self.mean=0
        self.breakeven=0
        self.minimum_buy_margin=0
        self.minimum_sell_margin=0
        self.stoploss_hit_flag=False
        self.open=0
        self.close=0
        self.high=0
        self.low=0
        self.trend_analysis=""
        self.buy_trend=""
        self.sell_trend=""

    # no need to be tested
    def start_next_iteration(self):
        self.loop-=1
        if (self.loop>0):
            self.logging.warning("Starting next iteration:"+str(self.loop))
            self.reset_variables()
            self.set_loop_indicators()
            self.init_kite_and_price_pointers()
            self.price_checker("PriceMonitorThread",self.delay,self.stock)
        else:
            self.logging.warning("No iteration Pending:"+str(self.loop))

    ######################################
    ### Unit Test Implimented - 100%
    ######################################
    def set_indicators_after_buy(self):
        self.buy_trend=self.trend_analysis
        self.trailing_margin_amt=self.sl_price_buy*self.traling_margin_percentage/100
        self.minimum_sell_margin=self.sl_price_buy + (self.trailing_margin_amt + self.breakeven)
        self.sl_price_sell=(self.sl_price_buy*(100-self.sl_margin_percentage)/100)
        #self.display_all_variables()

    ######################################
    ### Unit Test Implimented - 100%
    ######################################
    def set_indicators_after_sell(self):
        self.sell_trend=self.trend_analysis
        self.trailing_margin_amt=self.sl_price_sell*self.traling_margin_percentage/100
        self.minimum_buy_margin=self.sl_price_sell- (self.trailing_margin_amt + self.breakeven)
        self.sl_price_buy=(self.sl_price_sell*(100+self.sl_margin_percentage)/100)
        #self.display_all_variables()

    # Unit Test Implimented for this function
    def buy_stock(self,ltp,order_type="MARKET"):
        buy_permission=keyring.get_password("zerodha","buy_permission")
        try:
            if buy_permission == 'True':
                self.logging.info("buying {} at price {} initial stoploss {} quantity::{}".format(self.stock,self.sl_price_buy,self.sl_price_sell,self.quantity))
                order_id=self.kite_login.place_order(tradingsymbol=self.stock,
                                        quantity=self.quantity,
                                        price=ltp,
                                        transaction_type="BUY",
                                        trigger_price=None,
                                        stoploss=None,
                                        order_type=order_type,
                                        validity=self.validity,
                                        product=self.product,
                                        variety=self.variety)
                self.wait_for_order_completion_buy(order_id)
                self.update_buy_and_sell_to_file("Buy")
                self.update_loop_indicators("BuyCompleted")
                self.set_indicators_after_buy()
            else:
                self.logging.info("Buy permission is {} skipping buy".format(buy_permission))
        except Exception as e:
            self.logging.error("skipping buy due to below error...!!")
            self.logging.error(e, exc_info=True)
            raise Exception()

    # Unit Test Implimented for this function
    def sell_stock(self,ltp,order_type="MARKET"):
        sell_permission=keyring.get_password("zerodha","sell_permission")
        try:
            if sell_permission == 'True':
                order_id=self.kite_login.place_order(tradingsymbol=self.stock,
                                        quantity=self.quantity,
                                        price=ltp,
                                        transaction_type="SELL",
                                        trigger_price=None,
                                        stoploss=None,
                                        order_type=order_type,
                                        validity=self.validity,
                                        product=self.product,
                                        variety=self.variety)
                self.wait_for_order_completion_sell(order_id)
                self.update_buy_and_sell_to_file("Sell")
                self.update_loop_indicators("SellCompleted")
                self.set_indicators_after_sell()
            else:
                self.logging.info("Sell permission is {} skipping sell".format(sell_permission))
        except Exception as e:
            self.logging.error("skipping sell due to below error....!!")
            self.logging.error(e, exc_info=True)
            raise Exception()

    ######################################
    ### Unit Test Check Derived Class
    ######################################
    def init_price_pointers_buy(self,ltprice):
        pass

    ######################################
    ### Unit Test Check Derived Class
    ######################################
    def init_price_pointers_sell(self,ltprice):
        pass

    ######################################
    ### Unit Test Check Derived Class
    ######################################
    def init_margin_price_pointers(self,ltprice):
        pass

    ######################################
    ### Unit Test Check Derived Class
    ######################################
    def set_price(self,ltp):
        pass

    ######################################
    ### Unit Test Check Derived Class
    ######################################
    def price_action(self,ltp):
        pass


    # no need of unit testing
    def show_variables(self,ltp):
        #self.trend="\u25bc\u25bc\u25bc\u25bc"
        #self.trend="\u25b2\u25b2\u25b2\u25b2"
        #self.trend_analysis=keyring.get_password("zerodha",self.stock)
        self.counter=self.counter+1
        self.profit_margin=0
        style="$"*80+"\n"
        line_four="Mean:{:6}\tProfit: {:6}\t\tCount: {:5}\t\tList:{:4}\n".format(round(self.mean,2),round(self.profit,2),self.counter,len(self.lt_price_list))
        #line_five="Deviations\tMean:{}\t\tStd Dev: {}\t\tVariance: {}\n".format(round(self.mean_diff,2),round(self.std_diff,2),round(self.var_diff,2))
        line_five="High:{:6}\tLow: {:6}\t\tOpen: {:6}\t\tClose: {:6}\n".format(self.high,self.low,self.open,self.close)
        if(self.buy_flag):
            line_one="Buying\t\tsl_buy: {:6}\t\tltprice: {:6}\t\tStock: {:6}\n".format(round(self.sl_price_buy,2),ltp,self.stock)
            line_two="Indicators\tmin_buy: {:6}\t\ttrail_amt: {:6}\tINDEX: {:8}\n".format(round(self.minimum_buy_margin,2),round(self.trailing_margin_amt,2),self.kite_login.index)
            line_three="{:10}\tBuy: {}\t\tSell: {}\t\tsell: {:6}\n".format(self.type,self.buy_flag,self.sell_flag,round(self.sl_price_sell,2))

        elif(self.sell_flag):
            line_one="Selling\t\tsl_sell: {:6}\t\tltprice: {:6}\t\tStock: {:6}\n".format(round(self.sl_price_sell,2),ltp,self.stock)
            line_two="Indicators\tmin_sell: {:6}\ttrail_amt: {:6}\tINDEX: {:8}\n".format(round(self.minimum_sell_margin,2),round(self.trailing_margin_amt,2),self.kite_login.index)
            line_three="{:10}\tBuy: {}\t\tSell: {}\t\tbuy: {:6}\n".format(self.type,self.buy_flag,self.sell_flag,round(self.sl_price_buy,2))
        self.logging.info("Delay:"+str(self.delay)+"\n\n"+style+line_one+line_two+line_three+line_four+line_five+style)



'''

    def show_variables(self,ltp):
        #self.trend="\u25bc\u25bc\u25bc\u25bc"
        #self.trend="\u25b2\u25b2\u25b2\u25b2"
        #self.trend_analysis=keyring.get_password("zerodha",self.stock)
        self.counter=self.counter+1
        self.profit_margin=0
        style="$"*80+"\n"
        line_four="Mean:{}\tProfit: {}\t\tCount: {}\t\tList:{}\n".format(round(self.mean,2),round(self.profit,2),self.counter,len(self.lt_price_list))
        #line_five="Deviations\tMean:{}\t\tStd Dev: {}\t\tVariance: {}\n".format(round(self.mean_diff,2),round(self.std_diff,2),round(self.var_diff,2))
        line_five="High:{}\tLow: {}\t\tOpen: {}\t\tClose: {}\n".format(self.high,self.low,self.open,self.close)
        if(self.buy_flag):
            line_one="Buying\t\tsl_buy: {}\t\tltprice: {}\t\tStock: {}\n".format(round(self.sl_price_buy,2),ltp,self.stock)
            line_two="Indicators\tmin_buy: {}\t\ttrail_amt: {}\t\tTrend: {}\n".format(round(self.minimum_buy_margin,2),round(self.trailing_margin_amt,2),self.trend_analysis)
            line_three="{}\tBuy: {}\t\tSell: {}\t\tsell: {}\n".format(self.type,self.buy_flag,self.sell_flag,round(self.sl_price_sell,2))

        elif(self.sell_flag):
            line_one="Selling\t\tsl_sell: {}\t\tltprice: {}\t\tStock: {}\n".format(round(self.sl_price_sell,2),ltp,self.stock)
            line_two="Indicators\tmin_sell: {}\t\ttrail_amt: {}\t\tTrend: {}\n".format(round(self.minimum_sell_margin,2),round(self.trailing_margin_amt,2),self.trend_analysis)
            line_three="{}\tBuy: {}\t\tSell: {}\t\tbuy: {}\n".format(self.type,self.buy_flag,self.sell_flag,round(self.sl_price_buy,2))
        self.logging.info("Delay:"+str(self.delay)+"\n\n"+style+line_one+line_two+line_three+line_four+line_five+style)

    def display_all_variables(self):
        display_str="delay::{}\nstock::{}\nquantity::{}\nexchange::{}\ntype::{}\nsl_margin_percentage::{}\ntraling_margin_percentage::{}\nrunning::{}\nbuy_flag::{}\nsell_flag::{}\nvalidity::{}\nproduct::{}\nvariety::{}\nsl_price_buy::{}\nsl_price_sell::{}\nminimum_sell_margin::{}\ntrailing_margin_amt::{}"
        self.logging.warning(display_str.format(self.delay,   self.stock,    self.quantity,    self.exchange,    self.type,    self.sl_margin_percentage,    self.traling_margin_percentage,    self.running,    self.buy_flag,    self.sell_flag,    self.validity,    self.product,    self.variety,self.sl_price_buy,self.sl_price_sell,self.minimum_sell_margin,self.trailing_margin_amt))

    def display_all_variables(self):
        display_str="delay::{}\nstock::{}\nquantity::{}\nexchange::{}\ntype::{}\nsl_margin_percentage::{}\ntraling_margin_percentage::{}\nrunning::{}\nbuy_flag::{}\nsell_flag::{}\nvalidity::{}\nproduct::{}\nvariety::{}\nsl_price_buy::{}\nsl_price_sell::{}\nminimum_sell_margin::{}\ntrailing_margin_amt::{}"
        self.logging.warning(display_str.format(self.delay,   self.stock,    self.quantity,    self.exchange,    self.type,    self.sl_margin_percentage,    self.traling_margin_percentage,    self.running,    self.buy_flag,    self.sell_flag,    self.validity,    self.product,    self.variety,self.sl_price_buy,self.sl_price_sell,self.minimum_sell_margin,self.trailing_margin_amt))


    # Unit Test Implimented for this function
    def buy_stock_mock(self,ltp):
        buy_permission=keyring.get_password("zerodha","buy_permission")
        try:
            if buy_permission == 'True':
                self.logging.info("buying {} at price {} initial stoploss {} quantity::{}".format(self.stock,self.sl_price_buy,self.sl_price_sell,self.quantity))
                self.sl_price_buy=ltp
                self.update_buy_and_sell_to_file("Buy")
                self.update_loop_indicators("BuyCompleted")
                self.set_indicators_after_buy()
            else:
                self.logging.info("Buy permission is {} skipping buy".format(buy_permission))
        except Exception as e:
            self.logging.error("skipping buy due to below error...!!")
            self.logging.error(e, exc_info=True)
            raise Exception(e)

    # Unit Test Implimented for this function
    def sell_stock_mock(self,ltp):
        sell_permission=keyring.get_password("zerodha","sell_permission")
        try:
            if sell_permission == 'True':
                self.sl_price_sell=ltp
                self.update_buy_and_sell_to_file("Sell")
                self.update_loop_indicators("SellCompleted")
                self.set_indicators_after_sell()
            else:
                self.logging.info("Sell permission is {} skipping sell".format(sell_permission))
        except Exception as e:
            self.logging.error("skipping sell due to below error....!!")
            self.logging.error(e, exc_info=True)
            raise Exception(e)
'''
