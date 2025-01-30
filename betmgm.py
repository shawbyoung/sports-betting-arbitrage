from driver import *

class betmgm(driver):
	def __init__(self):		
		super().__init__('betmgm')
 
	def _login_aux(self):
		self.driver.get('https://sports.mi.betmgm.com/en/sports')

	def _get_promotion_link(self) -> str:
		match util.promotion:
			case 'nba':
				return 'https://sports.mi.betmgm.com/en/sports/basketball-7/betting/usa-9/nba-6004'
			case _:
				assert False, f'{util.promotion} undefined in {self.name}'

	def _get_events(self):
		table_css_selector = 'grid-event-wrapper'
		WebDriverWait(self.driver, 10).until(
			EC.presence_of_element_located((By.CLASS_NAME, table_css_selector))
		)
		time.sleep(1)

		events = self.driver.find_elements(By.CLASS_NAME, table_css_selector)

		return events

	def _parse_event(self, event):
		try:
			info = event.find_element(By.CLASS_NAME, 'grid-info-wrapper')
			participants = [participant_div.text for participant_div in info.find_elements(By.CLASS_NAME, 'participant')]
		except:
			self._log('Could not find participants.', 'error')
			return None

		if len(participants) != 2:
			self._log('Event dropped, participants len neq 2.', 'error')
			return None

		event_odds_div = event.find_element(By.CLASS_NAME, 'grid-group-container')
		if not event_odds_div:
			self._log('Event dropped, no grid container.', 'error')
			return None

		betting_categories_wrappers = event_odds_div.find_elements(By.CLASS_NAME, 'grid-option-group')
		if len(betting_categories_wrappers) != 3:
			self._log('Event dropped, # of elements in event grid neq 3.', 'error')
			return None
		
		spread = betting_categories_wrappers[0].text.split()
		total = betting_categories_wrappers[1].text.split()
		moneyline = betting_categories_wrappers[2].text.split()

		return odds(self.name, participants, spread, total, moneyline)