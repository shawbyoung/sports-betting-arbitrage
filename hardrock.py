from driver import *

class hardrock(driver):
    def __init__(self):
        super().__init__('HardRock')
        self.promotions = {
            'nba'
        }

    async def _login_aux(self):
        self.driver.get('https://app.hardrock.bet/')

    async def _collect_nba_odds(self):
        self.driver.get('https://app.hardrock.bet/sport-leagues/basketball/691033199537586178')

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'hr-outright-tab-content-container'))
            )
            time.sleep(1)
            events_parent_div = self.driver.find_element(By.CLASS_NAME, 'hr-outright-tab-content-container')
        except:
            logger.log_warning(f'[{self.name}][NBA] No events loaded.')
            return []
                
        events = events_parent_div.find_elements(By.XPATH, "./*")

        odds = []
        for div in events[1:]:
            participants = [participant_div.text for participant_div in div.find_elements(By.CLASS_NAME, 'participant')] 
            if len(participants) != 2:
                logger.log_warning(f'[{self.name}][NBA] Event dropped, participants len neq 2.')
                continue

            betting_categories_wrappers = div.find_elements(By.CLASS_NAME, 'selection-result')
            
            spread = betting_categories_wrappers[0].text.split()
            total = betting_categories_wrappers[1].text.split()
            moneyline = betting_categories_wrappers[2].text.split()

            event_odds = self._create_event_odds(participants, spread, total, moneyline)

            if event_odds:
                odds.append(self._create_event_odds(participants, spread, total, moneyline))

        return odds