from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class HomePage(BasePage):

    def scroll_select(self, country_name):
        """
        Returns a locator tuple that scrolls the UIAutomator view to the element
        with the given visible text (country name).
        """
        return (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiScrollable(new UiSelector()).scrollIntoView(text("{country_name}"))'
        )

    # Legacy wrapper to maintain compatibility with older test code
    def Scroll_Select(self, country_name):
        """Alias for select_country to preserve old API."""
        self.select_country(country_name)

    name_field = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("com.androidsample.generalstore:id/nameField")')
    male_radio = (AppiumBy.XPATH, "//android.widget.RadioButton[@text='Male']")
    shop_button = (AppiumBy.ID, "com.androidsample.generalstore:id/btnLetsShop")

    def select_country(self, country_name):
        """
        Opens the country dropdown and scrolls to the desired country,
        then selects it.
        """
        # Open Country Dropdown
        self.driver.find_element(
            AppiumBy.ID,
            "com.androidsample.generalstore:id/spinnerCountry"
        ).click()

        # Locate the country using the scroll_select helper and click it
        self.driver.find_element(*self.scroll_select(country_name)).click()
    def enter_name(self, name):
        # Wait for main activity to be loaded
        self.driver.wait_activity("com.androidsample.generalstore.MainActivity", 6)
        # Wait until the name field is visible and then send keys
        element = WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located(self.name_field)
        )
        element.send_keys(name)

    def select_male(self):
        self.driver.find_element(*self.male_radio).click()

    def click_shop(self):
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable(self.shop_button)
        ).click()
