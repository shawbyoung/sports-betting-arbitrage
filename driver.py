import time
import util
from itertools import chain
from logger import logger
from odds import odds
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from typing import Callable

class driver:
	def __init__(self, name):
		self.name = name
		self._log(f'Initializing web driver.')
		self.driver = webdriver.Chrome()

	def driver_quit(self) -> None:
		self._log(f'Quitting web driver.')
		self.driver.quit()

	def _log(self, log_type: str | None = None, message: str = None, level: int | None = None) -> None:
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

	def _get_promotion_link(self, promotion: str):
		pass 

	# Gets the appropriate promotion page for `collect_promotion_odds`. 
	def _get_promotion_page(self, promotion: str):
		try:
			self.driver.get(self.promotion_link(promotion))
		except:
			self._log('error', f'Cannot get {promotion} page from {self.name}.')

	# Returns elements that represent sports events.
	def _get_events(self, promotion: str):
		pass

	# Parses an element and returns odds.
	def _parse_event(self, event):
		pass

	# Generic function for collecting odds from a promotion after getting the 
 	# appropriate promotion link.
	def get_odds(self, promotion: str):
		self._get_promotion_page(promotion)
		events = self._get_events(promotion)
		odds = []
		for event in events:
			event_odds = self._parse_event(promotion, event)
			if event_odds:
				odds.append(event_odds)
		return odds