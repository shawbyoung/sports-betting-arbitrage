from driver import *

class betrivers(driver):
    def __init__(self):
        super().__init__('betrivers')

    def _login_aux(self):
        wait_time = 5
        self.driver.get('https://mi.betrivers.com/?page=sportsbook&feed=featured#home')

        login_button_by, login_button_value = By.XPATH, '//*[@id="rsi-top-navigation"]/header[1]/div/div[2]/button[1]'
        util.simulate.wait_for_element(self.driver, wait_time, login_button_by, login_button_value)
        login_button = self.driver.find_element(login_button_by, login_button_value)
        util.simulate.click_short_wait(login_button)

        username_input_by, username_input_value = By.ID, "login-form-modal-email"
        password_input_by, password_input_value = By.ID, "login-form-modal-password"
        submit_button_by, submit_button_value = By.ID, "login-form-modal-submit"
        util.simulate.wait_for_element(self.driver, wait_time, username_input_by, username_input_value)
        util.simulate.wait_for_element(self.driver, wait_time, password_input_by, password_input_value)
        util.simulate.wait_for_element(self.driver, wait_time, submit_button_by, submit_button_value)

        username_input = self.driver.find_element(username_input_by, username_input_value)
        password_input = self.driver.find_element(password_input_by, password_input_value)
        submit_button = self.driver.find_element(submit_button_by, submit_button_value)

        '''
        Checks the state of username_input and password_input and greedily clicks the login button if 
        validation-ok exists in both elements, assuming cookies have loaded in the username and password.
        Waits for valdiation attributes to load.
        '''
        util.simulate.exact_wait(2.5)
        valid_user_entered = "validation-ok" in username_input.get_attribute("class").split()
        valid_password_entered = "validation-ok" in password_input.get_attribute("class").split()
        if valid_user_entered and valid_password_entered:
            self._log('Assuming cookies have loaded in username and password - submitting login form.')
            util.simulate.click_short_wait(submit_button)
        else:
            self._log('Entering information into login form.')
            self._login_form_entry(username_input, password_input, submit_button)
        util.simulate.exact_wait(5)

    def _get_promotion_link(self) -> str:
        match util.promotion:
            case 'nba':
                return 'https://mi.betrivers.com/?page=sportsbook&group=1000093652&type=matches#home'
            case _:
                assert False, f'{util.promotion} undefined in {self.get_name()}'

    def _get_events_aux(self) -> list[WebElement]:
        # TODO: lowkey this selector is so ugly surely there's a better way to do this.
        table_css_selector = 'div[data-testid=\'listview-group-1000093652-events-container\''
        events_parent_div = self._safe_driver_wait(By.CSS_SELECTOR, table_css_selector, 10)
        if events_parent_div is None:
            return []
        return self._safe_driver_get_all(By.CSS_SELECTOR, 'article')

    def _strip_event(self, event: WebElement) -> tuple:
        try:
            # TODO: soooo ugly, replace when u can.
            event_elements = event.find_element(By.XPATH, './div').find_elements(By.XPATH, './div')[0].find_elements(By.XPATH, './div')[0].find_elements(By.XPATH, './div')
            participants_wrapper = (event_elements[1]).find_element(By.XPATH, './div').find_element(By.XPATH, './div').find_elements(By.XPATH, './div')
            betting_categories_wrapper = (event_elements[3]).find_element(By.XPATH, './div').find_elements(By.XPATH, './div')
        except Exception as e:
            self._log(f'Event could not be stripped. {e}', 'error')
            return None, None

        return participants_wrapper, betting_categories_wrapper

    def _participants_parser(self, participants_wrapper) -> list[str]:
        participants: list[str] = []
        for participant_div in participants_wrapper:
            participant_str_li: list[str] = participant_div.text.split()[1:]
            # During live games, the participant string may contain the score, remove it.
            if participant_str_li[-1].isnumeric():
                participant_str_li.pop()
            participants.append(' '.join(participant_str_li))
        return participants

    def _construct_odds(self, participants_wrapper, betting_categories_wrapper) -> odds | None:
        participants: list[str] = self._participants_parser(participants_wrapper)
        moneyline: list[str] = betting_categories_wrapper[1].text.split()
        return odds.construct_odds(self._name, participants, moneyline)

    def _get_moneyline_bet_button_aux(self, event: WebElement, team: str) -> WebElement | None:
        participants_wrapper, betting_categories_wrapper = self._strip_event(event)
        if not participants_wrapper or not betting_categories_wrapper:
            return None
        participants: list[str] = self._participants_parser(participants_wrapper)
        if len(participants) != 2 or (team not in participants[0] and team not in participants[1]):
            self._log(f'Malformed `participants`. {participants}', 'error')
            return None
        team_idx: int = 0 if team in participants[0] else 1
        if len(betting_categories_wrapper) != 3:
            self._log(f'Malformed `betting_categories_wrapper`. {betting_categories_wrapper}', 'error')
            return None
        moneyline_element: WebElement = betting_categories_wrapper[1]
        try:
            return moneyline_element.find_elements(By.XPATH, './button')[team_idx]
        except Exception as e:
            self._log(f'Could not find moneyline bet button. Exception: {e}', 'error')
            return None

    def _get_bet_slip_element_aux(self) -> WebElement | None:
        bet_slip_by, bet_slip_value = By.CLASS_NAME, "mod-KambiBC-betslip-container"
        util.simulate.wait_for_element(self.driver, 1, bet_slip_by, bet_slip_value)
        return self.driver.find_element(bet_slip_by, bet_slip_value)

    def _get_wager_input_element_aux(self, bet_slip_element) -> WebElement | None:
        wager_element_by, wager_element_value = By.CLASS_NAME, "mod-KambiBC-stake-input"
        util.simulate.wait_for_element(self.driver, 1, wager_element_by, wager_element_value)
        return self.driver.find_element(wager_element_by, wager_element_value)

    def _get_submit_bet_button_aux(self, bet_slip_element) -> WebElement | None:
        submit_button_by, submit_button_value = By.CLASS_NAME, "mod-KambiBC-betslip__place-bet-btn"
        util.simulate.wait_for_element(self.driver, 1, submit_button_by, submit_button_value)
        return self.driver.find_element(submit_button_by, submit_button_value)

    def _get_bet_slip_odds_element_aux(self, bet_slip_element) -> WebElement | None:
        odds_by, odds_value = By.CLASS_NAME, "mod-KambiBC-betslip-outcome__odds"
        util.simulate.wait_for_element(self.driver, 1,  odds_by, odds_value )
        odds = self.driver.find_elements(odds_by, odds_value)
        if len(odds) != 1:
            raise Exception('Number of bet slip odds elements neq 1')
        return odds[0]