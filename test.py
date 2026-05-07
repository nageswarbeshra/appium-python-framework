# import os
#
#
# # username = os.environ.get('username')
# import getpass
# import re
#
# user_ = os.environ.get('USERNAME')
# formatted_name = re.sub(r'\d*\$$', '', user_).replace('-', '.').lower()
# appium_path = f"C:\\Users\\" + formatted_name + "\\AppData\\Roaming\\npm\\appium"
#
#
# app_path  = os.getcwd()+"\\resources\\General-Store.apk"
# print(app_path)
import os

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import time

# Step 1 : Import Appium Service class
from appium.webdriver.appium_service import AppiumService

# Step 2 : Create object for Appium Service class
appium_service = AppiumService()

# Step 3 : Call Start method by using Appium Service class object
appium_service.start()

# Step 4 : Create "Desired Capabilities"
app_path  = os.getcwd()+"\\resources\\General-Store.apk"
desired_caps = {}
desired_caps['platformName'] = 'Android'
desired_caps['automationName'] = 'UiAutomator2'
desired_caps['app'] = app_path

options = UiAutomator2Options().load_capabilities(desired_caps)
driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", options=options)

ele_id = driver.find_element(AppiumBy.ID, "com.code2lead.kwad:id/EnterValue")
ele_id.click()

time.sleep(5)
driver.quit()

# Step 5 : Call stop method by using Appium Service class object
appium_service.stop()