from driver import *

class draftkings(driver):
	def __init__(self):		
		super().__init__('draftkings')
		self.promotions = {
			'nba'
		}
 
	def _login_aux(self):
		self.driver.get('https://sports.mi.betmgm.com/en/sports')

	def _get_promotion_page(self, promotion):
		match promotion:
			case 'nba':
				self.driver.get('https://sportsbook.draftkings.com/leagues/basketball/nba')
			case _:
				assert False, f'{promotion} undefined in {self.name}'

	def _get_events(self, promotion: str):
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
			self._log('warning', 'No events loaded.')
			return []

	def _parse_event(self, promotion, event):
		try:
			participants = [team.find_element(By.CLASS_NAME, 'event-cell__name-text').text for team in event]
		except:
			self._log_promotion(promotion, 'error', 'Could not find participants.')
			return None

		if len(participants) != 2:
			self._log_promotion(promotion, 'error', 'Event dropped, participants len neq 2.')
			return None

		# if checking for len eq 3 for td's
		moneyline = [team.find_elements(By.CSS_SELECTOR, 'td[class="sportsbook-table__column-row"]')[2].text for team in event]		
		spread = []
		total = []

		return odds(promotion, participants, spread, total, moneyline)