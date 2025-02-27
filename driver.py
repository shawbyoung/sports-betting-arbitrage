import time
import util

from itertools import chain
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from typing import Callable

from logger import logger
from odds import odds

class driver:
	def __init__(self, name):
		self.name = name
		self._username = None
		self._password = None
		self._user_data_dir = None

	def set_user_data_dir(self, user_data_dir):
		self._user_data_dir = user_data_dir

	def initialize_webdriver(self) -> None:
		self._log(f'Initializing {self.name} web driver.')
		self._log(f'Using \'{self._user_data_dir}\' as user_data_dir.')
		service = Service(executable_path=util.chromedriver_path, service_args=['--log-level=DEBUG'])
		options = Options()
		user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0"
		options.add_argument(f"user-agent={user_agent}")
		options.binary_location = 'chrome/chrome-win64/chrome.exe'
		options.add_argument(f'--user-data-dir={self._user_data_dir}')
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
		self.password = password

	def set_username(self, username) -> None:
		self.username = username
		self._log(f'Set username = {username}.')

	def driver_quit(self) -> None:
		self._log(f'Quitting web driver.')
		self.driver.quit()

	def _log(self, message: str = '', log_type: str | None = None, level: int | None = None) -> None:
		log_fn_str = f'log_{log_type}' if log_type else 'log'
		log_fn = getattr(logger, log_fn_str, None)
		assert log_fn, '"log"\'s types should be defined.'

		if not level:
			log_fn(f'[{self.name}] {message}')
			return

		log_fn(f'[{self.name}] {message}', level)

	def _login_form_entry(self, username_input, password_input, submit_button):
		util.simulate.short_interaction_time()
		util.simulate.type_in_field(username_input, self.username)
		util.simulate.short_interaction_time()
		util.simulate.type_in_field(password_input, self.password)
		util.simulate.click_short_wait(submit_button)

	def _login_aux(self) -> None:
		self.driver.get('www.example.com')

	def login(self) -> bool:
		for idx in range(util.max_login_retries):
			self._log(f'Log in attempt {idx}.')
			try:
				self._login_aux()
				self._log(f'Logged in.')
				return True
			except Exception as e:
				self._log(f'Failed to log in. {e}')
				util.simulate.exact_wait(10)
		return False

	def _get_promotion_link(self):
		pass

	# Gets the appropriate promotion page for `collect_promotion_odds`. 
	# Logs an error if the page is unreachable.
	def _get_promotion_page(self) -> bool:
		try:
			link = self._get_promotion_link()
			cur_url = self.driver.current_url
			if link != cur_url:
				self.driver.get(self._get_promotion_link())
			return True
		except Exception as e:
			self._log(f'Cannot get {util.promotion} page. {e}', 'error')
			return False

	def _get_events_aux(self):
		pass

	# Returns elements that represent sports events.
	def _get_events(self):
		try:
			events = self._get_events_aux()
			self._log(f'Found {len(events)} events.')
			return events
		except Exception as e:
			self._log(f'Failed to load events. {e}', 'warning')
			return []

	# Parses an element and returns odds.
	def _parse_event(self, event):
		pass

	# Generic function for collecting odds from a promotion after getting the 
 	# appropriate promotion link.
	def get_odds(self):
		if not self._get_promotion_page():
			return []

		events = self._get_events()
		odds = []
		for event in events:
			event_odds = self._parse_event(event)
			if event_odds:
				odds.append(event_odds)
		return odds

	def _get_event_element(self, team):
		events = self._get_events()
		for event in events:
			if event.text.contains(team):
				return event
		return None

	def _get_moneyline_bet_button(self, event, team):
		return None

	def execute_bet(self, team, wager) -> bool:
		if not self._get_promotion_page():
			return False

		event = self._get_event_element(team)
		if not event:
			return False

		button = self._get_moneyline_bet_button(event, team)
		if not button:
			return False

		button.click()
		return True