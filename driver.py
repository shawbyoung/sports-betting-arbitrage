import time
import util

from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from typing import Callable, Type, TypeVar

from logger import logger
from odds import odds
from bet_request import bet_request
from bet_slip import bet_slip

class driver:
	def __init__(self, name):
		self._name = name
		self._username = None
		self._password = None
		self._user_data_dir = None
		self._active_bet_request: bet_request = None
		self._active_bet_slip: bet_slip = None

	def get_name(self):
		return self._name

	def _set_active_bet_slip(self, bet_slip: bet_slip):
		self._active_bet_slip = bet_slip

	def get_active_bet_slip(self) -> bet_slip:
		return self._active_bet_slip

	def get_active_bet_request(self) -> bet_request | None:
		return self._active_bet_request

	def set_active_bet_request(self, active_bet_request: bet_request):
		self._active_bet_request = active_bet_request

	def set_user_data_dir(self, user_data_dir):
		self._user_data_dir = user_data_dir

	def initialize_webdriver(self) -> None:
		self._log(f'Initializing {self.get_name()} web driver.')
		self._log(f'Using \'{self._user_data_dir}\' as user_data_dir.')
		service = Service(executable_path=util.chromedriver_path(), service_args=['--log-level=DEBUG'])
		options = Options()
		options.binary_location = 'chrome/chrome-win64/chrome.exe'
		options.page_load_strategy = 'eager'
		prefs = {"profile.default_content_setting_values.geolocation": 1}
		options.add_experimental_option("prefs", prefs)
		user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0"
		options.add_argument(f"user-agent={user_agent}")
		options.add_argument('--ignore-certificate-errors')
		options.add_argument(f'--user-data-dir={self._user_data_dir}')
		options.add_argument('--start-maximized')
		options.add_argument('--disable-blink-features')
		options.add_argument('--disable-blink-features=AutomationControlled')
		options.add_experimental_option("excludeSwitches", ["enable-automation"])
		options.add_experimental_option('useAutomationExtension', False)
		options.add_argument("--no-sandbox")
		self.driver = webdriver.Chrome(service=service, options=options)
		self._log(f'Initialized web driver.')
		self.driver.execute_script(
			"Object.defineProperty(navigator, 'webdriver', {"
				"get: () => undefined"
			"})"
		)
		navigator_webdriver = self.driver.execute_script("return navigator.webdriver;")
		if navigator_webdriver:
			self._log(f'Webdriver NOT set to undefined, set to {navigator_webdriver}. Detection possible.')
			exit(1)
		self._log(f'Executed scripts.')

	def set_password(self, password) -> None:
		self._password = password

	def set_username(self, username) -> None:
		self._username = username
		self._log(f'Set username = {username}.')

	def get_username(self) -> str:
		return self._username

	def _get_password(self) -> str:
		return self._password

	def driver_quit(self) -> None:
		self._log(f'Quitting web driver.')
		self.driver.quit()

	def _log(self, message: str = '', log_type: str | None = None, level: int | None = None) -> None:
		log_fn_str = f'log_{log_type}' if log_type else 'log'
		log_fn = getattr(logger, log_fn_str, None)
		assert log_fn, '"log"\'s types should be defined.'

		if not level:
			log_fn(f'[{self.get_name()}] {message}')
			return

		log_fn(f'[{self.get_name()}] {message}', level)

	# TODO: make calls to `_login_form_entry` safer via failing if false. This could require
	# the reworking of login and deciding on a more philisophical question - do we try-catch
	# in utilty functions or outside of them? I lean towards within, avoid code duplicity.
	# Argument to be made that failing with a call stack is helpful? Worth exploring later.
	def _login_form_entry(self, username_input, password_input, submit_button) -> bool:
		util.simulate.short_interaction_time()
		if not util.simulate.type_in_field(username_input, self.get_username()):
			self._log('Failed to type in username.', 'error')
			return False
		util.simulate.short_interaction_time()
		if not util.simulate.type_in_field(password_input, self._get_password()):
			self._log('Failed to type in password.', 'error')
			return False
		util.simulate.click_short_wait(submit_button)
		return True

	def _login_aux(self) -> None:
		self.driver.get('www.example.com')

	def login(self) -> bool:
		if not self.get_username():
			self._log(f'No username configured.', 'error')
			return False
		if not self._get_password():
			self._log(f'No password configured.', 'error')
			return False
		for idx in range(util.max_login_retries()):
			self._log(f'Log in attempt {idx}.')
			try:
				self._login_aux()
				self._log(f'Logged in.')
				return True
			except Exception as e:
				self._log(f'Failed to log in. {e}')
				util.simulate.exact_wait(5)
		return False

	def _get_promotion_link(self):
		pass

	# Gets the appropriate promotion page for `collect_promotion_odds`. 
	# Logs an error if the page is unreachable.
	# TODO: consider re-requesting the same link, betmgm seemed to maintain different
	# odds from what appeared on the bet slip. a refreshed fixed this.
	def _get_promotion_page(self) -> bool:
		try:
			if self._get_promotion_link() !=  self.driver.current_url:
				self.driver.get(self._get_promotion_link())
			return True
		except Exception as e:
			self._log(f'Cannot get {util.promotion} page. {e}', 'error')
			return False

	def _get_events_aux(self) -> list[WebElement]:
		pass

	# Returns elements that represent sports events.
	def _get_events(self) -> list[WebElement]:
		try:
			events: list[WebElement] = self._get_events_aux()
			self._log(f'Found {len(events)} events.')
			return events
		except Exception as e:
			self._log(f'Failed to load events. {e}', 'warning')
			return []

	# Strips an event down to a participants_wrapper and a betting_categories_wrapper.
	def _strip_event(self, event: WebElement) -> tuple:
		pass

	# TODO: decide on typing for participants wrapper and betting_categories_wrapper. probably just list[WebElement].
	# Constructs an odds object (or returns None) from a participants_wrapper and a betting_categories_wrapper.
	def _construct_odds(self, participants_wrapper, betting_categories_wrapper) -> odds | None:
		pass

	# Parses an element and returns odds.
	def _parse_event(self, event) -> odds | None:
		participants_wrapper, betting_categories_wrapper = self._strip_event(event)

		if not participants_wrapper or not betting_categories_wrapper:
			self._log('Event dropped, _strip_event returned None for at least one of participants_wrapper, betting_categories_wrapper.', 'warning')
			return None

		if len(participants_wrapper) != 2:
			self._log('Event dropped, participants len neq 2.', 'warning')
			return None

		if len(betting_categories_wrapper) != 3:
			self._log('Event dropped, betting_categories_wrapper len neq 3.', 'warning')
			return None

		return self._construct_odds(participants_wrapper, betting_categories_wrapper)

	# Generic function for collecting odds from a promotion after getting the 
 	# appropriate promotion link.
	def get_odds(self) -> list[odds]:
		if not self._get_promotion_page():
			return []

		events: list[WebElement] = self._get_events()
		all_odds: list[odds] = []
		for event in events:
			event_odds: odds = self._parse_event(event)
			if event_odds:
				all_odds.append(event_odds)
		return all_odds

	def _get_event_element(self, team: str) -> WebElement | None:
		events: list[WebElement] = self._get_events()
		for event in events:
			if team in event.text:
				return event
		return None

	def _safe_driver_get(self, by: str, value: str) -> WebElement | None:
		try:
			return self.driver.find_element(by, value)
		except Exception as e:
			self._log(f'Could not find element {{by: {by}, value: {value}}}. Exception: {e}', 'error')
			return None

	def _safe_driver_get_all(self, by: str, value: str) -> list[WebElement]:
		try:
			return self.driver.find_elements(by, value)
		except Exception as e:
			self._log(f'Could not find elements {{by: {by}, value: {value}}}. Exception: {e}', 'error')
			return []

	def _safe_driver_wait(self, by: str, value: str, timeout: int) -> WebElement | None:
		try:
			return WebDriverWait(self.driver, timeout).until(
				EC.presence_of_element_located((by, value))
			)
		except Exception as e:
			self._log(f'Could not find element {{by: {by}, value: {value}}}. Exception: {e}', 'error')
			return None

	def _get_web_element(self, *args: ..., aux_fn: Callable[..., WebElement], error_message: str) -> WebElement | None:
		res: WebElement | None = None
		exception: Exception | None = None
		try:
			res = aux_fn(*args)
		except Exception as e:
			exception = e
		if not res:
			self._log(error_message + f' Exception: {exception}' if exception else error_message)
		return res

	def _get_moneyline_bet_button(self, event: WebElement, team: str) -> WebElement | None:
		return self._get_web_element(
			event, team,
			aux_fn=self._get_moneyline_bet_button_aux,
			error_message='Couldn\'t get moneyline bet button.')

	def _get_moneyline_bet_button_aux(self, event: WebElement, team: str) -> WebElement | None:
		return None

	def _get_bet_slip_element(self) -> WebElement | None:
		return self._get_web_element(
			aux_fn=self._get_bet_slip_element_aux,
			error_message='Couldn\'t get bet slip element.'
		)

	def _get_bet_slip_element_aux(self) -> WebElement | None:
		return None

	def _get_wager_input_element(self, bet_slip_element: WebElement) -> WebElement | None:
		return self._get_web_element(
			bet_slip_element,
			aux_fn=self._get_wager_input_element_aux,
			error_message='Couldn\'t get wager input element.'
		)

	def _get_wager_input_element_aux(self, bet_slip_element: WebElement) -> WebElement | None:
		return None

	def _get_submit_bet_button(self, bet_slip_element: WebElement) -> WebElement | None:
		return self._get_web_element(
			bet_slip_element,
			aux_fn=self._get_submit_bet_button_aux,
			error_message='Couldn\'t get submit bet button.'
		)

	def _get_submit_bet_button_aux(self, bet_slip_element: WebElement) -> WebElement | None:
		return None

	def _get_bet_slip_odds_element(self, bet_slip_element: WebElement) -> WebElement | None:
		return self._get_web_element(
			bet_slip_element,
			aux_fn=self._get_bet_slip_odds_element_aux,
			error_message='Couldn\'t get bet slip odds element.'
		)

	def _get_bet_slip_odds_element_aux(self, bet_slip_element: WebElement) -> WebElement | None:
		return None

	def prepare_bet(self, mock: bool) -> bool:
		br: bet_request | None = self.get_active_bet_request()
		if not br:
			self._log('No active bet request.', 'error')
			return False
		if not self._get_promotion_page():
			return False

		# Finds and clicks the appropriate moneyline bet button.
		event_element: WebElement = self._get_event_element(br.get_team())
		if not event_element:
			self._log(f'Couldn\'t find event element corresponding to {br.get_team()}.', 'error')
			return False
		button: WebElement = self._get_moneyline_bet_button(event_element, br.get_team())
		if not button:
			self._log(f'Couldn\'t get moneyline bet button. Could be inactive', 'error')
			return False
		if not mock:
			if not util.simulate.safe_click(self.driver, button):
				return False

		# TODO: more meaningful disambiguation with multiple bets on slip for
		# `_get_wager_input` and `_get_bet_slip_odds_element`.
		# Prepares bet slip information for final verification and execution.
		# Instruction ordering is particular - at least on betrivers, there is a tendency for the bet_slip
		# element to disappear. This should call for safer utility functions (surrounded by try catch blocks
		# with a return value representing success.). For now, simply interacting with the bet slip element
		# quickly appears to help prevent it from disappearing.
		# It's possible previous runs of prepare bet change the state - more reason to implement the epilogue.

		bet_slip_element: WebElement = self._get_bet_slip_element()
		if not bet_slip_element:
			return False

		wager_input_element: WebElement = self._get_wager_input_element(bet_slip_element)
		if not wager_input_element:
			return False

		if not mock:
			if not util.simulate.clear_and_type_in_field(wager_input_element, str(br.get_wager())):
				self._log(f'Failed to enter wager amount in input.')
				return False

		active_bet_bet_slip_odds_element: WebElement = self._get_bet_slip_odds_element(bet_slip_element)
		if not active_bet_bet_slip_odds_element:
			return False

		submit_bet_button: WebElement = self._get_submit_bet_button(bet_slip_element)
		if not submit_bet_button:
			return False

		self._set_active_bet_slip(
			bet_slip(
				bet_slip_element,
				active_bet_bet_slip_odds_element,
				wager_input_element,
				submit_bet_button))
		return True

	def execute_bet(self, mock: bool) -> bool:
		br: bet_request = self.get_active_bet_request()
		bs: bet_slip = self.get_active_bet_slip()
		try:
			bs_odds: str = bs.get_odds_element().text
			prefix, odds = bs_odds[0], bs_odds[1:]
			if prefix not in ['+', '-'] or not odds.isnumeric():
				raise Exception(f'Odds string formatted incorrectly. {bs_odds}')
			if util.american.to_decimal(bs_odds) != br.get_odds():
				raise Exception(f'Bet slip odds ({util.american.to_decimal(bs_odds)}={bs_odds}) neq bet request odds ({br.get_odds()})')
			if mock:
				return True
			return util.simulate.safe_click(self.driver, bs.get_submit_button())
		except Exception as e:
			logger.log_error(str(e))
			return False

task_res_ty = TypeVar('task_res_ty')
driver_to_task_res_opt_ty = dict[Type[driver], task_res_ty | None]
task_ty = Callable[[Type[driver]], task_res_ty]

class drivers:
	stringmap = dict[str, Type[driver]]

	def run_on_drivers(task: task_ty, drivers: list[driver]):
		results: driver_to_task_res_opt_ty = {}
		if len(drivers) == 0:
			logger.log_error('No drivers.')
			return results

		with ThreadPoolExecutor(max_workers=len(drivers)) as executor:
			future_to_driver = {executor.submit(task, d): d for d in drivers}
			for future in as_completed(future_to_driver):
				driver_obj: driver = future_to_driver[future]
				try:
					results[driver_obj] = future.result()
				except Exception as e:
					logger.log_error(f"Error with driver {driver_obj}: {e}")
					results[driver_obj] = None

		return results