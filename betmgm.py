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