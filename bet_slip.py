class bet_slip:
    def __init__(self, web_element, odds_element, wager_input_element, submit_button):
        self._web_element = web_element
        self._odds_element = odds_element
        self._wager_input_element = wager_input_element
        self._submit_button = submit_button

    def get_web_element(self):
        return self._web_element

    def get_odds_element(self):
        return self._odds_element

    def get_wager_input_element(self):
        return self._wager_input_element

    def get_submit_button(self):
        return self._submit_button