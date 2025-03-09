from selenium.webdriver.remote.webelement import WebElement

class bet_slip:
    def __init__(self, web_element, odds_element, wager_input_element, submit_button):
        self._web_element: WebElement = web_element
        self._odds_element: WebElement = odds_element
        self._wager_input_element: WebElement = wager_input_element
        self._submit_button: WebElement = submit_button

    def get_web_element(self) -> WebElement:
        return self._web_element

    def get_odds_element(self) -> WebElement:
        return self._odds_element

    def get_wager_input_element(self) -> WebElement:
        return self._wager_input_element

    def get_submit_button(self) -> WebElement:
        return self._submit_button