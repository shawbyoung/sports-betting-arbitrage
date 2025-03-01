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

	def _get_events_aux(self):
		table_css_selector = 'grid-event-wrapper'
		WebDriverWait(self.driver, 10).until(
			EC.presence_of_element_located((By.CLASS_NAME, table_css_selector))
		)
		time.sleep(1)

		events = self.driver.find_elements(By.CLASS_NAME, table_css_selector)
		return events

	def _strip_event(self, event):
		try:
			participants_wrapper = event.find_element(By.CLASS_NAME, 'grid-info-wrapper').find_elements(By.CLASS_NAME, 'participant')
			betting_categories_wrapper = event.find_element(By.CLASS_NAME, 'grid-group-container').find_elements(By.CLASS_NAME, 'grid-option-group')
		except Exception as e:
			self._log(f'Event could not be stripped. {e}', 'error')
			return None

		return participants_wrapper, betting_categories_wrapper

	def _construct_odds(self, participants_wrapper, betting_categories_wrapper) -> odds | None:
		participants = [participant_div.text for participant_div in participants_wrapper]
		moneyline = betting_categories_wrapper[2].text.split()
		return odds.construct_odds(self.get_name(), participants, moneyline)

	def _get_moneyline_bet_button_aux(self, event, team):
		participants_wrapper, betting_categories_wrapper = self._strip_event(event)
		participants = [participant_div.text for participant_div in participants_wrapper]
		team_idx = 0 if team in participants[0] else 1
		moneyline_element = betting_categories_wrapper[2]
		return moneyline_element.find_elements(By.CSS_SELECTOR, 'ms-event-pick')[team_idx]

	def _get_bet_slip_element_aux(self):
		bet_slip_by, bet_slip_value = By.CLASS_NAME, "bet-column"
		util.simulate.wait_for_element(self.driver, 1, bet_slip_by, bet_slip_value)
		return self.driver.find_element(bet_slip_by, bet_slip_value)

	def _get_wager_input_element_aux(self, bet_slip_element):
		wager_element_by, wager_element_value = By.CLASS_NAME, "stake-input-value"
		util.simulate.wait_for_element(self.driver, 1, wager_element_by, wager_element_value)
		return self.driver.find_element(wager_element_by, wager_element_value)

	def _get_submit_bet_button_aux(self, bet_slip_element):
		submit_button_by, submit_button_value = By.CLASS_NAME, "betslip-place-button"
		util.simulate.wait_for_element(self.driver, 1, submit_button_by, submit_button_value)
		return self.driver.find_element(submit_button_by, submit_button_value)

	def _get_bet_slip_odds_element_aux(self, bet_slip_element):
		odds_by, odds_value = By.CLASS_NAME, "betslip-pick-odds__value"
		util.simulate.wait_for_element(self.driver, 1,  odds_by, odds_value )
		odds = self.driver.find_elements(odds_by, odds_value)
		if len(odds) != 1:
			raise Exception('Number of bet slip odds elements neq 1')
		return odds[0]
