from driver import *

class betrivers(driver):
    def __init__(self):
        super().__init__('betrivers')

    def _login_aux(self):
        self.driver.get('https://mi.betrivers.com/?page=sportsbook&feed=featured#home')

    def _get_promotion_link(self) -> str:
        match util.promotion:
            case 'nba':
                return 'https://mi.betrivers.com/?page=sportsbook&group=1000093652&type=matches'
            case _:
                assert False, f'{util.promotion} undefined in {self.name}'

    def _get_events(self):
        try:
            table_css_selector = 'div[data-testid=\'listview-group-1000093652-events-container\''            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, table_css_selector))
            )
            time.sleep(1)
            events_parent_div = self.driver.find_element(By.CSS_SELECTOR, table_css_selector)
            events = events_parent_div.find_elements(By.CSS_SELECTOR, 'article')
            self._log(f'Found {len(events)} events.')
            return events
        except Exception as e:
            self._log(f'Failed to load events. {e}', 'warning')
            return []

    def _parse_event(self, event):
        try:
            event_elements = event.find_element(By.XPATH, './div').find_elements(By.XPATH, './div')[0].find_elements(By.XPATH, './div')[0].find_elements(By.XPATH, './div')
            participants_wrapper = (event_elements[1]).find_element(By.XPATH, './div').find_element(By.XPATH, './div').find_elements(By.XPATH, './div')
            participants = [participant_div.text.split()[1] for participant_div in participants_wrapper]
        except Exception as e:
            self._log(f'Could not find participants. {e}', 'error')
            return None

        if len(participants) != 2:
            self._log('Event dropped, participants len neq 2.', 'warning')
            return None

        betting_categories_wrapper = (event_elements[3]).find_element(By.XPATH, './div').find_elements(By.XPATH, './div')
        spread = betting_categories_wrapper[0].text.split()
        total = betting_categories_wrapper[2].text.split()
        moneyline = betting_categories_wrapper[1].text.split()

        return odds(self.name, participants, spread, total, moneyline)