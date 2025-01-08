import asyncio
import time
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
	
	async def _collect_nba_odds(self):
		pass