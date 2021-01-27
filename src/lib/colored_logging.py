import os
import logging
from datetime import datetime
dir_path = os.path.dirname(os.path.realpath(__file__))




#, filemode='a', format='[%(filename)s:%(lineno)s ] %(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""


    def __init__(self,name="noname"):
        self.filename=str(dir_path)+os.path.sep+".."+os.path.sep+".."+os.path.sep+"logs"+os.path.sep+"app"+datetime.now().strftime("_%Y_%b_%d_%H_%M_%S")+"_"+name+".log"

    green = "\033[92m"
    cyan ='\033[36m'
    grey = "\x1b[38;21m"
    yellow = "\033[93m"
    red = "\033[91m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"

    FORMATS = {
        logging.DEBUG: cyan + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

    def get_logger(self,app_name,level):
        logger = logging.getLogger(app_name)
        logger.setLevel(level)
        sh=logging.StreamHandler()
        sh.setLevel(level)
        sh.setFormatter(CustomFormatter())
        logger.addHandler(sh)
        ch = logging.FileHandler(self.filename)
        ch.setLevel(level)
        ch.setFormatter(CustomFormatter())
        logger.addHandler(ch)


        return logger


    class fg:
        black='\033[30m'
        red='\033[31m'
        green='\033[32m'
        orange='\033[33m'
        blue='\033[34m'
        purple='\033[35m'
        cyan='\033[36m'
        lightgrey='\033[37m'
        darkgrey='\033[90m'
        lightred='\033[91m'
        lightgreen='\033[92m'
        yellow='\033[93m'
        lightblue='\033[94m'
        pink='\033[95m'
        lightcyan='\033[96m'
    class bg:
        black='\033[40m'
        red='\033[41m'
        green='\033[42m'
        orange='\033[43m'
        blue='\033[44m'
        purple='\033[45m'
        cyan='\033[46m'
        lightgrey='\033[47m'


if __name__ == "__main__":
    log=CustomFormatter().get_logger("Test",0)
    log.debug("\n\n\n")
    log.debug("A quirky message only developers care about")
    log.debug("A quirky message only developers care about")
    log.debug("A quirky message only developers care about")
    log.debug("A quirky message only developers care about")
    log.info("Curious users might want to know this")
    log.info("Curious users might want to know this")
    log.info("Curious users might want to know this")
    log.info("Curious users might want to know this")
    log.info("Curious users might want to know this")
    log.warn("Something is wrong and any user should be informed")
    log.warn("Something is wrong and any user should be informed")
    log.warn("Something is wrong and any user should be informed")
    log.warn("Something is wrong and any user should be informed")
    log.warn("Something is wrong and any user should be informed")
    log.error("Serious stuff, this is red for a reason")
    log.error("Serious stuff, this is red for a reason")
    log.error("Serious stuff, this is red for a reason")
    log.error("Serious stuff, this is red for a reason")
    log.error("Serious stuff, this is red for a reason")
    log.critical("OH NO everything is on fire")
    log.critical("OH NO everything is on fire")
    log.critical("OH NO everything is on fire")
    log.critical("OH NO everything is on fire")
    log.critical("OH NO everything is on fire")
