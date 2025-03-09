from driver import *

class betmgm(driver):
	def __init__(self):		
		super().__init__('betmgm')
 
	def _login_aux(self):
		wait_time = 5
		self.driver.get('https://www.mi.betmgm.com/en/labelhost/login')

		username_input_by, username_input_value = By.ID, "userId"
		password_input_by, password_input_value = By.NAME, "password"
		submit_button_by, submit_button_value = By.XPATH, '//*[@id="login"]/form/fieldset/section/div/button'
		util.simulate.wait_for_element(self.driver, wait_time, username_input_by, username_input_value)
		util.simulate.wait_for_element(self.driver, wait_time, password_input_by, password_input_value)
		util.simulate.wait_for_element(self.driver, wait_time, submit_button_by, submit_button_value)

		username_input = self.driver.find_element(By.ID, "userId")
		password_input = self.driver.find_element(By.NAME, "password")
		submit_button = self.driver.find_element(By.XPATH, '//*[@id="login"]/form/fieldset/section/div/button')

		'''
		Interacts with page to activate submission button if cookies have loaded in username and password.
		Greedily clicks login button if enabled assuming cookies have loaded in username and password.
		'''
		util.simulate.click_short_wait(password_input)
		if not submit_button.get_attribute("disabled"):
			self._log('Assuming cookies have loaded in username and password - submitting login form.')
			util.simulate.click_short_wait(submit_button)
		else:
			self._login_form_entry(username_input, password_input, submit_button)
		util.simulate.exact_wait(5)

	def _get_promotion_link(self) -> str:
		match util.promotion:
			case 'nba':
				return 'https://sports.mi.betmgm.com/en/sports/basketball-7/betting/usa-9/nba-6004'
			case _:
				assert False, f'{util.promotion} undefined in {self.get_name()}'

	def _get_events_aux(self) -> list[WebElement]:
		_ = self._safe_driver_wait(By.CLASS_NAME, 'grid-event-wrapper', 10)
		return self._safe_driver_get_all(By.CLASS_NAME, 'grid-event-wrapper')

	def _strip_event(self, event: WebElement) -> tuple:
		try:
			participants_wrapper: WebElement = (
				event.find_element(By.CLASS_NAME, 'grid-info-wrapper')
					 .find_elements(By.CLASS_NAME, 'participant')
			)
			betting_categories_wrapper: WebElement = (
				event.find_element(By.CLASS_NAME, 'grid-group-container')
					 .find_elements(By.CLASS_NAME, 'grid-option-group')
			)
			return participants_wrapper, betting_categories_wrapper
		except Exception as e:
			self._log(f'Event could not be stripped. {e}', 'error')
			return None, None

	def _participants_parser(self, participants_wrapper) -> list[str]:
		return [participant_div.text for participant_div in participants_wrapper]

	def _construct_odds(self, participants_wrapper, betting_categories_wrapper) -> odds | None:
		participants: list[str] = self._participants_parser(participants_wrapper)
		moneyline: list[str] = betting_categories_wrapper[2].text.split()
		return odds.construct_odds(self.get_name(), participants, moneyline)

	def _get_moneyline_bet_button_aux(self, event: WebElement, team: str) -> WebElement | None:
		participants_wrapper, betting_categories_wrapper = self._strip_event(event)
		if not participants_wrapper or not betting_categories_wrapper:
			return None
		participants: list[str] = self._participants_parser(participants_wrapper)
		if len(participants) != 2 or (team not in participants[0] and team not in participants[1]):
			self._log(f'Malformed `participants`. {participants}', 'error')
			return None
		team_idx: int = 0 if team in participants[0] else 1
		if len(betting_categories_wrapper) != 3:
			self._log(f'Malformed `betting_categories_wrapper`. {betting_categories_wrapper}', 'error')
			return None
		moneyline_element: WebElement = betting_categories_wrapper[2]
		try:
			return moneyline_element.find_elements(By.CSS_SELECTOR, 'ms-event-pick')[team_idx]
		except Exception as e:
			self._log(f'Could not find moneyline button. {e}', 'error')
			return None

	def _get_bet_slip_element_aux(self) -> WebElement | None:
		bet_slip_by: str = By.CLASS_NAME
		bet_slip_value: str = 'bet-column'
		return self._safe_driver_wait(bet_slip_by, bet_slip_value, 1)

	def _get_wager_input_element_aux(self, bet_slip_element: WebElement) -> WebElement | None:
		wager_element_by: str = By.CLASS_NAME
		wager_element_value: str = "stake-input-value"
		return self._safe_driver_wait(wager_element_by, wager_element_value, 1)

	def _get_submit_bet_button_aux(self, bet_slip_element) -> WebElement | None:
		submit_button_by: str = By.CLASS_NAME
		submit_button_value: str = 'betslip-place-button'
		return self._safe_driver_wait(submit_button_by, submit_button_value, 1)

	def _get_bet_slip_odds_element_aux(self, bet_slip_element):
		odds_by: str = By.CLASS_NAME
		odds_value: str = 'betslip-pick-odds__value'
		self._safe_driver_wait(odds_by, odds_value, 1)
		odds = self._safe_driver_get_all(odds_by, odds_value)
		if len(odds) != 1:
			raise Exception('Number of bet slip odds elements neq 1')
		return odds[0]
