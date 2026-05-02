from appium import webdriver
from appium.options.android import UiAutomator2Options
from config.desired_caps import caps


def get_driver(port):
    # Appium server should be started once per test session (handled by fixture)
    options = UiAutomator2Options().load_capabilities(caps)

    driver = webdriver.Remote(
        command_executor=f"http://127.0.0.1:{port}",
        options=options
    )
    driver.implicitly_wait(10)
    return driver