import asyncio
import time
import util
from itertools import chain
from logger import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class driver:
	def __init__(self, name):
		self.name = name
		logger.log(f'Initializing {self.name} web driver.')
		self.driver = webdriver.Firefox()
		self.promotions = {}

	def driver_quit(self):
		logger.log(f'Quitting {self.name} web driver.')
		self.driver.quit()

	async def _login_aux(self):
		self.driver.get('www.example.com')

	async def login(self):
		logger.log(f'Logging into {self.name}.')
		await self._login_aux()
		logger.log(f'Logged into {self.name}.')

	async def collect_odds(self, promotions):
		odds = []
		requested_promotions = [p for p in self.promotions if p in promotions] 
		coros = [getattr(self, f'_collect_{p}_odds')() for p in requested_promotions]
		odds = await asyncio.gather(*coros)
		return list(chain.from_iterable(odds))
	
	def _create_event_odds(self, participants, spread, total, moneyline):
		total_idx = 1
		if participants[0] < participants[1]:
			t1_participants_idx = 0
			t2_participants_idx = 1
			t1_spread_idx = 1
			t2_spread_idx = 3
			t1_total_idx = 2
			t2_total_idx = 5
			t1_moneyline_idx = 0
			t2_moneyline_idx = 1
		else:
			t1_participants_idx = 1
			t2_participants_idx = 0
			t1_spread_idx = 3
			t2_spread_idx = 1
			t1_total_idx = 5
			t2_total_idx = 2
			t1_moneyline_idx = 1
			t2_moneyline_idx = 0

		t1_name = participants[t1_participants_idx]
		t2_name = participants[t2_participants_idx]

		event_odds = {
			'sportsbook' : self.name,
			't1_name' : t1_name,
			't2_name' : t2_name
		}

		if len(spread) == 4:
			event_odds['t1_spread_odds'] = util.american.to_decimal(spread[t1_spread_idx])
			event_odds['t2_spread_odds'] = util.american.to_decimal(spread[t2_spread_idx])
		else:
			logger.log_warning(f'[{self.name}][NBA] {t1_name}, {t2_name} event has no spread info.')

		if len(total) == 6:
			event_odds['total_score'] = total[total_idx]
			event_odds['t1_total_odds'] = util.american.to_decimal(total[t1_total_idx])
			event_odds['t2_total_odds'] = util.american.to_decimal(total[t2_total_idx])
		else:
			logger.log_warning(f'[{self.name}][NBA] {t1_name}, {t2_name} event has no total info.')

		if len(moneyline) == 2:
			event_odds['t1_moneyline_odds'] = util.american.to_decimal(moneyline[t1_moneyline_idx])
			event_odds['t2_moneyline_odds'] = util.american.to_decimal(moneyline[t2_moneyline_idx])
		else:
			logger.log_warning(f'[{self.name}][NBA] {t1_name}, {t2_name} event has no moneyline info, dropping.')
			return None

		return event_odds

	async def _collect_nba_odds(self):
		pass