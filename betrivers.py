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
        '''
        valid_user_entered = "validation-ok" in username_input.get_attribute("class").split()
        valid_password_entered = "validation-ok" in password_input.get_attribute("class").split()
        if valid_user_entered and valid_password_entered:
            self._log('Assuming cookies have loaded in username and password - submitting login form.')
            util.simulate.click_short_wait(submit_button)
        else:
            self._login_form_entry(username_input, password_input, submit_button)
        util.simulate.exact_wait(5)

    def _get_promotion_link(self) -> str:
        match util.promotion:
            case 'nba':
                return 'https://mi.betrivers.com/?page=sportsbook&group=1000093652&type=matches#home'
            case _:
                assert False, f'{util.promotion} undefined in {self.get_name()}'

    def _get_events_aux(self):
        table_css_selector = 'div[data-testid=\'listview-group-1000093652-events-container\''
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, table_css_selector))
        )
        time.sleep(1)

        events_parent_div = self.driver.find_element(By.CSS_SELECTOR, table_css_selector)
        events = events_parent_div.find_elements(By.CSS_SELECTOR, 'article')

        return events

    def _strip_event(self, event):
        try:
            event_elements = event.find_element(By.XPATH, './div').find_elements(By.XPATH, './div')[0].find_elements(By.XPATH, './div')[0].find_elements(By.XPATH, './div')
            participants_wrapper = (event_elements[1]).find_element(By.XPATH, './div').find_element(By.XPATH, './div').find_elements(By.XPATH, './div')
        except Exception as e:
            self._log(f'Could not find participants. {e}', 'error')
            return None, None

        betting_categories_wrapper = (event_elements[3]).find_element(By.XPATH, './div').find_elements(By.XPATH, './div')
        return participants_wrapper, betting_categories_wrapper

    def _parse_event(self, event) -> odds:
        # TODO: fix how participants are parsed, we were parsing "Trail" for some portland trailblazer game.
        participants_wrapper, betting_categories_wrapper = self._strip_event(event)

        if not participants_wrapper or not betting_categories_wrapper:
            self._log('Event dropped, _strip_event returned None for at least one of participants_wrapper, betting_categories_wrapper.', 'warning')
            return None

        participants = [participant_div.text for participant_div in participants_wrapper]

        if len(participants) != 2:
            self._log('Event dropped, participants len neq 2.', 'warning')
            return None

        moneyline = betting_categories_wrapper[1].text.split()

        return odds.construct_odds(self._name, participants, moneyline)

    def _get_moneyline_bet_button(self, event, team):
        participants_wrapper, betting_categories_wrapper = self._strip_event(event)
        participants = [participant_div.text.split()[1] for participant_div in participants_wrapper]
        team_idx = 0 if team in participants[0] else 1
        moneyline_element = betting_categories_wrapper[1]
        return moneyline_element.find_elements(By.XPATH, './button')[team_idx]