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
		logger.log(f'Initializing {self.name} web driver.')
		self.driver = webdriver.Firefox()
		self.promotions = {}

	def driver_quit(self) -> None:
		logger.log(f'Quitting {self.name} web driver.')
		self.driver.quit()

	def _log(self, type: str, message: str, level: int | None) -> None:
		log = getattr(logger, f'log_{type}', None)
		assert log, '"log"\'s type should be defined.'

		if level == None:
			log(f'[{self.name}] {message}')
			return

		log(f'[{self.name}] {message}', level)

	def _log_promotion(
     	self, promotion: str, type: str, message: str, level: int | None
	) -> None:
		self._log(type, f'[{promotion}] {message}', level)

	def _login_aux(self) -> None:
		self.driver.get('www.example.com')

	def login(self) -> None:
		logger.log(f'Logging into {self.name}.')
		self._login_aux()
		logger.log(f'Logged into {self.name}.')

	def _get_promotion_link(self, promotion: str):
		pass 

	# Gets the appropriate promotion page for `collect_promotion_odds`. 
	def _get_promotion_page(self, promotion: str):
		try:
			self.driver.get(self.promotion_link(promotion))
		except:
			self._log_promotion(
       			promotion, 'error', f'Cannot get {promotion} page from {self.name}.'
          	)

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

	# async def collect_odds(self, promotions):
	# 	odds = []
	# 	requested_promotions = [p for p in self.promotions if p in promotions] 
	# 	coros = [getattr(self, f'_collect_{p}_odds')() for p in requested_promotions]
	# 	odds = await asyncio.gather(*coros)
	# 	return list(chain.from_iterable(odds))