import time
import util

from itertools import chain
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from typing import Callable

from logger import logger
from odds import odds

class driver:
	def __init__(self, name):
		self.name = name
		self.username = None
		self.password = None
		self.initialize_webdriver()

	def initialize_webdriver(self) -> None:
		self._log(f'Initializing web driver.')
		options = Options()
		options.add_argument('--disable-blink-features=AutomationControlled')
		options.add_experimental_option("excludeSwitches", ["enable-automation"])
		options.add_experimental_option('useAutomationExtension', False)
		self.driver = webdriver.Chrome(options=options)
		self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
		self._log(f'Initialized web driver.')

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
		assert log_fn, '"log"\'s type should be defined.'

		if not level:
			log_fn(f'[{self.name}] {message}')
			return

		log_fn(f'[{self.name}] {message}', level)

	def _login_aux(self) -> None:
		self.driver.get('www.example.com')

	def login(self) -> bool:
		self._log(f'Logging in.')
		try:
			self._login_aux()
		except Exception as e:
			self._log(f'Failed to log in. {e}')
			return True

		self._log(f'Logged in.')
		return False

	def _get_promotion_link(self):
		pass

	# Gets the appropriate promotion page for `collect_promotion_odds`. 
	# Logs an error if the page is unreachable.
	def _get_promotion_page(self):
		try:
			self.driver.get(self._get_promotion_link())
		except:
			self._log(f'Cannot get {util.promotion} page.', 'error')

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
		response = self._get_promotion_page()
		events = self._get_events()
		odds = []
		for event in events:
			event_odds = self._parse_event(event)
			if event_odds:
				odds.append(event_odds)
		return odds