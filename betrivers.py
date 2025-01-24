from driver import *

class betrivers(driver):
    def __init__(self):
        super().__init__('betrivers')
        self.promotions = {
            'nba'
        }

    async def _login_aux(self):
        self.driver.get('https://va.betrivers.com/?page=sportsbook&feed=featured#home')

    async def _collect_nba_odds(self):
        self.driver.get('https://va.betrivers.com/?page=sportsbook&group=1000093652&type=matches')

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(By.CSS_SELECTOR, "div[data-testid='listview-group-1000093652-events-container']")
            )
            time.sleep(1)
            events_parent_div = self.driver.find_element(By.CSS_SELECTOR, "div[data-testid='listview-group-1000093652-events-container']")
        except:
            self._log_nba('error', f'No events loaded.')
            return []
                
        events = events_parent_div.find_elements(By.CSS_SELECTOR, "data-testid='listview-group-1000093652-event-1021436135'")

        odds = []
        for div in events:
            try:
                participants_wrapper = div.find_element(By.CLASS_NAME, 'sc-jFAcUc.kXdfoS')
                participants = [participant_div.text for participant_div in participants_wrapper.find_elements(By.CLASS_NAME, 'sc-dbbhXq.fvsUMI')] 
            except:
                self._log_nba('error', 'Participants html element not found. Dropping event.')
                continue

            if len(participants) != 2:
                self._log_nba('warning', 'Event dropped, participants len neq 2.')
                continue

            betting_categories_wrappers = div.find_elements(By.CLASS_NAME, 'selection-result')
            
            spread = betting_categories_wrappers[0].text.split()
            total = betting_categories_wrappers[1].text.split()
            moneyline = betting_categories_wrappers[2].text.split()

            event_odds = self._create_event_odds(participants, spread, total, moneyline)

            if event_odds:
                odds.append(self._create_event_odds(participants, spread, total, moneyline))

        return odds