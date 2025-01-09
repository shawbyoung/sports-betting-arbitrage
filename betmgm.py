from driver import *

class betmgm(driver):
	def __init__(self):		
		super().__init__('MGM')
		self.promotions = {
			'nba'
		}

	async def _login_aux(self):
		self.driver.get('https://sports.va.betmgm.com/en/sports')

	async def _collect_nba_odds(self):
		self.driver.get('https://sports.va.betmgm.com/en/sports/basketball-7/betting/usa-9/nba-6004')
		try:
			WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.CLASS_NAME, 'grid-event-wrapper'))
			)
			time.sleep(1)
			events = self.driver.find_elements(By.CLASS_NAME, 'grid-event-wrapper')
		except:
			logger.log_warning(f'[{self.name}][NBA] No events loaded.')
			return []

		odds = []
		for div in events:
			info_div = div.find_element(By.CLASS_NAME, 'grid-info-wrapper')
			participants = [participant_div.text for participant_div in info_div.find_elements(By.CLASS_NAME, 'participant')] 

			if len(participants) != 2:
				logger.log_warning(f'[{self.name}][NBA] Event dropped, participants len neq 2.')
				continue

			event_odds_div = div.find_element(By.CLASS_NAME, 'grid-group-container')
			if not event_odds_div:
				logger.log_warning(f'[{self.name}][NBA] Event dropped, no grid container.')
				continue
			
			betting_categories_wrappers = event_odds_div.find_elements(By.CLASS_NAME, 'grid-option-group')
			if len(betting_categories_wrappers) != 3:
				logger.log_warning(f'[{self.name}][NBA] Event dropped, # of elements in event grid neq 3.')
				continue
			
			spread = betting_categories_wrappers[0].text.split()
			total = betting_categories_wrappers[1].text.split()
			moneyline = betting_categories_wrappers[2].text.split()

			event_odds = self._create_event_odds(participants, spread, total, moneyline)

			if event_odds:
				odds.append(event_odds)

		return odds