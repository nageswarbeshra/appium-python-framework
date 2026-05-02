import os.path

app_path  = os.getcwd()+"\\resources\\General-Store.apk"
caps = {
    "platformName": "Android",
    "automationName": "UiAutomator2",
    "deviceName": "Android Device",
    # "appPackage": "com.androidsample.generalstore",
    # "appActivity": "com.androidsample.generalstore.SplashActivity",
    "app":app_path
}