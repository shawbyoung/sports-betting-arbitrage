from driver import *

class fanduel(driver):
    def __init__(self):
        super().__init__('fanduel')

    def _login_aux(self):
        self.driver.get('https://account.mi.sportsbook.fanduel.com/login')
        username_input = self.driver.find_element(By.ID, 'login-email')
        password_input = self.driver.find_element(By.ID, 'login-password')
        submit_button = self.driver.find_element(By.CSS_SELECTOR, '[data-test-id="button-submit"]')
        self._login_form_entry(username_input, password_input, submit_button)

        util.simulate.exact_wait(5)

    def _get_promotion_link(self) -> str:
        match util.promotion:
            case 'nba':
                return 'https://mi.sportsbook.fanduel.com/navigation/nba'
            case _:
                assert False, f'{util.promotion} undefined in {self.name}'

    def _get_events(self):
        table_xpath = '/html/body/div[1]/div/div/div/div/div[2]/div[2]/main/div/div[1]/div/div[2]/div[3]/ul'
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, table_xpath))
        )
        time.sleep(1)

        events_parent_div = self.driver.find_element(By.CSS_SELECTOR, table_xpath)
        events = events_parent_div.find_elements(By.CSS_SELECTOR, 'li')

        return events

    def _parse_event(self, event):
        try:
            event_elements = event.find_element(By.XPATH, './div')
            # .find_elements(By.XPATH, './div')[0].find_elements(By.XPATH, './div')[0].find_elements(By.XPATH, './div')
            participants = (event_elements[0]).text.split()
        except Exception as e:
            self._log(f'Could not find participants. {e}', 'error')
            return None

        if len(participants) != 2:
            self._log('Event dropped, participants len neq 2.', 'warning')
            return None

        # betting_categories_wrapper = (event_elements[1]).find_element(By.XPATH, './div').find_elements(By.XPATH, './div')
        # spread = betting_categories_wrapper[0].text.split()
        # total = betting_categories_wrapper[2].text.split()
        # moneyline = betting_categories_wrapper[1].text.split()

        return odds(self.name, participants, [], [], [])
        # return odds(self.name, participants, spread, total, moneyline)
# 