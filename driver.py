import time
import util

from itertools import chain
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from typing import Callable

from logger import logger
from odds import odds

class driver:
	def __init__(self, name):
		self.name = name
		self._log(f'Initializing web driver.')
		self.driver = webdriver.Chrome()

	def driver_quit(self) -> None:
		self._log(f'Quitting web driver.')
		self.driver.quit()

	def _log(self, message: str = None, log_type: str | None = None, level: int | None = None) -> None:
		log_fn_str = f'log_{log_type}' if log_type else 'log'
		log_fn = getattr(logger, log_fn_str, None)
		assert log_fn, '"log"\'s type should be defined.'

		if not level:
			log_fn(f'[{self.name}] {message}')
			return

		log_fn(f'[{self.name}] {message}', level)

	def _login_aux(self) -> None:
		self.driver.get('www.example.com')

	def login(self) -> None:
		self._log(f'Logging in.')
		self._login_aux()
		self._log(f'Logged in.')

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