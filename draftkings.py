from driver import *

class draftkings(driver):
	def __init__(self):		
		super().__init__('draftkings')
 
	def _login_aux(self):
		self.driver.get('https://myaccount.draftkings.com/login')
		timeout = 5
		username_input = self._safe_driver_wait(By.ID, 'login-username-input', timeout)
		password_input = self._safe_driver_wait(By.ID, "login-password-input", timeout)
		submit_button = self._safe_driver_wait(By.ID, 'login-submit', timeout)

		# Clicks username_input to activate cookies if they exists.
		util.simulate.click_short_wait(username_input)
		util.simulate.click_short_wait(password_input)
		if (username_input.get_attribute("value") == self.get_username() and
			password_input.get_attribute("value") == self._get_password()):
			self._log('Cookies have loaded in username and password - submitting login form.')
			util.simulate.click_short_wait(submit_button)
		else:
			self._login_form_entry(username_input, password_input, submit_button)
		util.simulate.exact_wait(10)

	def _get_promotion_link(self) -> str:
		match util.promotion:
			case 'nba':
				return 'https://sportsbook.draftkings.com/leagues/basketball/nba'
			case _:
				assert False, f'{util.promotion} undefined in {self.name}'

	def _get_events_aux(self):
		table_by: str = By.CSS_SELECTOR
		table_value: str = 'tbody.sportsbook-table__body'
		if not self._safe_driver_wait(table_by, table_value, 10):
			return []
		sportsbook_tables = self.driver.find_elements(table_by, table_value)
		events = []
		for table in sportsbook_tables:
			table_rows = table.find_elements(By.CSS_SELECTOR, 'tr')
			for i in range(1, len(table_rows)-2, 2):
				events.append([table_rows[i], table_rows[i+1]])

		return events

	def _strip_event(self, event: WebElement) -> tuple:
		try:
			participants_wrapper = [team.find_element(By.CLASS_NAME, 'event-cell__name-text') for team in event]
			teams: list[WebElement] = [team.find_elements(By.CSS_SELECTOR, 'td.sportsbook-table__column-row') for team in event]
			betting_categories_wrapper = [[] for _ in range(len(teams[0]))]
			for team in teams:
				for idx, category in enumerate(team):
					betting_categories_wrapper[idx].append(category)
			return participants_wrapper, betting_categories_wrapper
		except Exception as e:
			self._log(f'Event could not be stripped. {e}', 'error')
			return None, None

	def _parse_participants(self, participants_wrapper) -> list[str]:
		return [participant.text for participant in participants_wrapper]

	def _parse_moneyline(self, betting_categories_wrapper) -> list[str]:
		try:
			return [team_moneyline.text for team_moneyline in betting_categories_wrapper[2]]
		except Exception as e:
			self._log(f'Moneyline could not be parsed. {e}', 'error')
			return None

	def _construct_odds(self, participants_wrapper, betting_categories_wrapper):
		participants = self._parse_participants(participants_wrapper)
		moneyline = self._parse_moneyline(betting_categories_wrapper)
		return odds.construct_odds(self.get_name(), participants, moneyline)

	def _get_event_element(self, team: str) -> WebElement | None:
		events: list[WebElement] = self._get_events()
		for event in events:
			for team_element in event:
				if team in team_element.text:
					return event
		return None

	def _get_moneyline_bet_button_aux(self, event: WebElement, team: str) -> WebElement | None:
		participants_wrapper, betting_categories_wrapper = self._strip_event(event)
		if not participants_wrapper or not betting_categories_wrapper:
			return None
		participants: list[str] = self._parse_participants(participants_wrapper)
		if len(participants) != 2 or (team not in participants[0] and team not in participants[1]):
			self._log(f'Malformed `participants`. {participants}', 'error')
			return None
		team_idx: int = 0 if team in participants[0] else 1
		if len(betting_categories_wrapper) != 3:
			self._log(f'Malformed `betting_categories_wrapper`. {betting_categories_wrapper}', 'error')
			return None
		try:
			return betting_categories_wrapper[2][team_idx]
		except Exception as e:
			self._log(f'Could not find moneyline button. {e}', 'error')
			return None

	def _get_bet_slip_element_aux(self) -> WebElement | None:
		bet_slip_by: str = By.CLASS_NAME
		bet_slip_value: str = 'sportsbook-betslip-accordion__wrapper'
		return self._safe_driver_wait(bet_slip_by, bet_slip_value, 1)

	def _get_wager_input_element_aux(self, bet_slip_element: WebElement) -> WebElement | None:
		wager_element_by: str = By.CLASS_NAME
		wager_element_value: str = "betslip-wager-box__input"
		return self._safe_driver_wait(wager_element_by, wager_element_value, 1)

	def _get_submit_bet_button_aux(self, bet_slip_element) -> WebElement | None:
		submit_button_by: str = By.CLASS_NAME
		submit_button_value: str = 'dk-place-bet-button__wrapper'
		return self._safe_driver_wait(submit_button_by, submit_button_value, 1)

	def _get_bet_slip_odds_element_aux(self, bet_slip_element):
		odds_by: str = By.CLASS_NAME
		odds_value: str = 'betslip-odds__display'
		self._safe_driver_wait(odds_by, odds_value, 1)
		odds = self._safe_driver_get_all(odds_by, odds_value)
		if len(odds) != 1:
			raise Exception('Number of bet slip odds elements neq 1')
		return odds[0]