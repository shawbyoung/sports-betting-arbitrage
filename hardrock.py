from driver import *

class hardrock(driver):
    def __init__(self):
        super().__init__('hardrock')
        self.promotions = {
            'nba'
        }

    def _login_aux(self):
        self.driver.get('https://app.hardrock.bet/')

    def _get_promotion_page(self, promotion):
        match promotion:
            case 'nba':
                self.driver.get('https://app.hardrock.bet/sport-leagues/basketball/691033199537586178')
            case _:
                assert False, f'{promotion} undefined in {self.name}'

    def _get_events(self, promotion: str):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'hr-outright-tab-content-container'))
            )
            time.sleep(1)
            return (self.driver.find_elements(By.CLASS_NAME, 'hr-outright-tab-content-container'))[1:]
        except:
            self._log_promotion(promotion, 'warning', 'No events loaded.')
            return []

    def _parse_event(self, promotion, event):
        participants = [participant_div.text for participant_div in event.find_elements(By.CLASS_NAME, 'participant')] 

        if len(participants) != 2:
            self._log_promotion(promotion, 'error', 'Event dropped, participants len neq 2.')
            return None

        betting_categories_wrappers = event.find_elements(By.CLASS_NAME, 'selection-result')
        
        spread = betting_categories_wrappers[0].text.split()
        total = betting_categories_wrappers[1].text.split()
        moneyline = betting_categories_wrappers[2].text.split()

        return odds(promotion, participants, spread, total, moneyline, self._log_promotion)