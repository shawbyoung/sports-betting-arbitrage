from driver import *

class betmgm(driver):
	def __init__(self):		
		super().__init__('betmgm')
 
	def _login_aux(self):
		self.driver.get('https://sports.mi.betmgm.com/en/sports')

	def _get_promotion_page(self, promotion):
		match promotion:
			case 'nba':
				self.driver.get('https://sports.mi.betmgm.com/en/sports/basketball-7/betting/usa-9/nba-6004')
			case _:
				assert False, f'{promotion} undefined in {self.name}'

	def _get_events(self, promotion: str):
		try:
			WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.CLASS_NAME, 'grid-event-wrapper'))
			)
			time.sleep(1)
			return self.driver.find_elements(By.CLASS_NAME, 'grid-event-wrapper')
		except:
			self._log('warning', 'No events loaded.')
			return []

	def _parse_event(self, promotion, event):
		try:
			info = event.find_element(By.CLASS_NAME, 'grid-info-wrapper')
			participants = [participant_div.text for participant_div in info.find_elements(By.CLASS_NAME, 'participant')]
		except:
			self._log('error', 'Could not find participants.')
			return None

		if len(participants) != 2:
			self._log('error', 'Event dropped, participants len neq 2.')
			return None

		event_odds_div = event.find_element(By.CLASS_NAME, 'grid-group-container')
		if not event_odds_div:
			self._log('error', 'Event dropped, no grid container.')
			return None

		betting_categories_wrappers = event_odds_div.find_elements(By.CLASS_NAME, 'grid-option-group')
		if len(betting_categories_wrappers) != 3:
			self._log('error', 'Event dropped, # of elements in event grid neq 3.')
			return None
		
		spread = betting_categories_wrappers[0].text.split()
		total = betting_categories_wrappers[1].text.split()
		moneyline = betting_categories_wrappers[2].text.split()

		return odds(self.name, promotion, participants, spread, total, moneyline)