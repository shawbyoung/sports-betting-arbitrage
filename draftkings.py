from driver import *
import util

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
			print(f'[draftkings] searching and waiting sportbook table')
			WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, 'table.sportsbook-table'))
			)
			time.sleep(1)
			print(f'[draftkings] waited, finding elements ')
			sportsbook_tables = self.driver.find_elements(By.CSS_SELECTOR, 'table.sportsbook-table')

			print(f'[draftkings] processsing elements')
			events = []
			for table in sportsbook_tables:
				table_rows = self.driver.find_elements(By.CSS_SELECTOR, 'tr')
				for i in range(0, len(table_rows), 2):
					events.append([table_rows[i], table_rows[i+1]]) 
			return events
		except:
			self._log('No events loaded.', 'warning')
			return []

	def _parse_event(self, event):
		try:
			participants = [team.find_element(By.CLASS_NAME, 'event-cell__name-text').text for team in event]
		except:
			self._log('Could not find participants.', 'error')
			return None

		if len(participants) != 2:
			self._log('Event dropped, participants len neq 2.', 'error')
			return None

		# if checking for len eq 3 for td's
		moneyline = [team.find_elements(By.CSS_SELECTOR, 'td[class="sportsbook-table__column-row"]')[2].text for team in event]		
		spread = []
		total = []

		return odds(self.name, participants, spread, total, moneyline)