import os


# username = os.environ.get('username')
import getpass
import re

user_ = os.environ.get('USERNAME')
formatted_name = re.sub(r'\d*\$$', '', user_).replace('-', '.').lower()
appium_path = f"C:\\Users\\" + formatted_name + "\\AppData\\Roaming\\npm\\appium"


app_path  = os.getcwd()+"\\resources\\General-Store.apk"
print(app_path)