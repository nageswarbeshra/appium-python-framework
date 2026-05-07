from pages.home_page import HomePage
from utilities.log_handler import nowLogs


class TestHome:

    def test_user_registration(self, driver):
        home = HomePage(driver)

        home.enter_name("Nageswar")
        nowLogs("Name entered")
        home.Scroll_Select("India")
        nowLogs("Country  Selected")
        home.select_male()
        nowLogs("Gender Selected")
        home.click_shop()
        nowLogs("Shop   button clicked")
        nowLogs("Button clicked")
        nowLogs("Button clicked")
