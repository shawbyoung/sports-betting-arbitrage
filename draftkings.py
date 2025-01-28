from driver import *

class draftkings(driver):
	def __init__(self):		
		super().__init__('draftkings')
 
	def _login_aux(self):
		self.driver.get('https://sports.mi.betmgm.com/en/sports')

	def _get_promotion_link(self) -> str:
		match util.promotion:
			case 'nba':
				return 'https://sportsbook.draftkings.com/leagues/basketball/nba'
			case _:
				assert False, f'{util.promotion} undefined in {self.name}'

	def _get_events(self):
		try:
			table_css_selector = 'tbody.sportsbook-table__body'
			WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, table_css_selector))
			)
			time.sleep(1)
			sportsbook_tables = self.driver.find_elements(By.CSS_SELECTOR, table_css_selector)

			events = []
			for table in sportsbook_tables:
				table_rows = self.driver.find_elements(By.CSS_SELECTOR, 'tr')
				for i in range(1, len(table_rows)-2, 2):
					events.append([table_rows[i], table_rows[i+1]]) 
			
			self._log(f'Found {len(events)} events.')
			return events
		except Exception as e:
			self._log(f'Failed to load events. {e}', 'warning')
			return []

	def _parse_event(self, event):
		try:
			raw_participants = [team.find_element(By.CLASS_NAME, 'event-cell__name-text').text for team in event]
			participants = [raw_participant.split()[1] for raw_participant in raw_participants]
		except:
			self._log('Could not find participants.', 'error')
			return None

		if len(participants) != 2:
			self._log('Event dropped, participants len neq 2.', 'error')
			return None

		moneyline = []
		for team in event:
			team_odds = team.find_elements(By.CSS_SELECTOR, 'td.sportsbook-table__column-row')
			# if checking for len eq 3 for td's
			moneyline.append(team_odds[2].text)

		spread = []
		total = []

		return odds(self.name, participants, spread, total, moneyline)