import os
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

dir_path = os.path.dirname(os.path.realpath(__file__))
home_path=dir_path.replace("src"+os.path.sep+"lib","")
sys.path.append(home_path)
driver_path=home_path+os.path.sep+"selenium"+os.path.sep+"chromedriver.exe"

class SeleniumUtil:
    delay=20
    sleep_time_in_sec=2
    def __init__(self, url,username,password,pin,show,logging):
        self.url = url
        self.username = username
        self.password = password
        self.pin = pin
        self.logging=logging
        try:
            if(show):
                self.driver=webdriver.Chrome(driver_path)
            else:
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-gpu")
                self.driver=webdriver.Chrome(driver_path,chrome_options=chrome_options)
            self.logging.debug("Successfully initialized selenium webdriver")
        except Exception as e:
            self.logging.error("Error initializing selenium webdriver :"+str(e))


    def login(self):
        try:
            self.driver.get(self.url)
            self.get_element_by_id("userid").send_keys(self.username)
            self.get_element_by_id("password").send_keys(self.password)
            self.get_element_by_xpath("//*[@id=\"container\"]/div/div/div/form/div[4]/button").click()
            time.sleep(self.sleep_time_in_sec)
            self.get_element_by_id("pin").send_keys(self.pin)
            self.get_element_by_xpath("//*[@id=\"container\"]/div/div/div/form/div[3]/button").click()
        except Exception as e:
            self.logging.error("Error fetching request_token from kite :"+str(e))


    def get_element_by_id(self,id):
        element = None
        try:
            element = WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.ID, id)))
        except e:
            self.logging.error("WebElement with id:"+str(id)+" causing read error :"+str(e))
            self.driver.quit()
        return element

    def get_element_by_xpath(self,xpath):
        element = None
        try:
            element = WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except e:
            self.logging.error("WebElement with xpath:"+str(xpath)+" causing read error :"+str(e))
            self.driver.quit()
        return element

    def get_request_token(self):
        self.login()
        time.sleep(self.sleep_time_in_sec)
        url_string=str(self.driver.current_url)
        self.logging.debug("url to getch request_token:"+str(url_string))
        request_token="ReadError"
        matches = ["?","&","request_token","="]
        if all(x in url_string for x in matches):
            params=url_string.split('?')[1].split('&')
            for data in params:
                if "request_token" in data:
                    request_token=data.split('=')[1]
                    break
        else:
            self.logging.error("No Matching pattern found while reading request_token: "+str(url_string))
        self.driver.quit()
        return request_token


#test()
