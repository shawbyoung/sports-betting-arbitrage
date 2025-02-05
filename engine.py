import json
import time
import os
import util

from itertools import chain
from concurrent.futures import ThreadPoolExecutor, as_completed

from driver import driver
from logger import logger

# Drivers
from betmgm import betmgm
from betrivers import betrivers
from draftkings import draftkings 
from hardrock import hardrock

class engine:
	def __init__(self):
		self.initalize_drivers()
		self.config()
		self.login()
		self.bet()
		self.epilogue()

	def initalize_drivers(self):
		os.environ['webdriver.chrome.driver'] = 'windows_executable/chromedriver.exe'
		self.drivers = {
			'betmgm' : betmgm(), 
			'draftkings' : draftkings(), 
			'betrivers' : betrivers()
		}

	def drop_sportsbook(self, sportsbook):
		if sportsbook not in self.drivers:
			logger.log(f'{sportsbook} not in drivers, unable to drop.')
			return

		self.drivers[sportsbook].driver_quit()
		del self.drivers[sportsbook]
		logger.log(f'Dropping sportbook {sportsbook}')

	def config(self):
		try:
			with open('.config', 'r') as file:
				config = json.load(file)
		except:
			logger.log_error('No config file.')
			exit(1)

		promotion_opt = config.get('promotion', None) 
		if not promotion_opt:
			logger.log_error('No promotion in config file.')
			exit(1)

		util.promotion = promotion_opt	
		logger.log(f'{util.promotion} selected as promotion.')

		sportsbooks_opt = config.get('sportsbooks', None)
		if not sportsbooks_opt:
			logger.log_error('No sportsbook information (username, password) in config file.')
			exit(1)

		for sportsbook_config in sportsbooks_opt:
			sportsbook = sportsbook_config.get('sportsbook', None)
			username = sportsbook_config.get('username', None)
			password = sportsbook_config.get('password', None)

			if not sportsbook:
				logger.log_error(f'No identifying sportsbook in sportsbook config entry.')
				exit(1)

			if sportsbook not in self.drivers:
				logger.log_error(f'{sportsbook} not in sportsbooks.')
				exit(1)

			if not username:
				logger.log_error(f'No username in {sportsbook} config .')
				exit(1)

			if not password:
				logger.log_error(f'No password in {sportsbook} config .')
				exit(1)

			self.drivers[sportsbook].set_username(username)
			self.drivers[sportsbook].password = password

	def _run_on_drivers(self, task, drivers):
		# TODO: implement me for bet execution
		pass

	def _run_on_all_drivers(self, task):
		results = {}
		with ThreadPoolExecutor(max_workers=len(self.drivers)) as executor:
			future_to_driver = {executor.submit(task, d): d for d in self.drivers.values()}
			for future in as_completed(future_to_driver):
				driver_obj = future_to_driver[future]
				try:
					results[driver_obj] = future.result()
				except Exception as e:
					logger.log_error(f"Error with driver {driver_obj}: {e}")
					results[driver_obj] = None

		return results

	def login(self):
		def task(d: driver):
			return d.login()
		logger.log('Logging into sportsbooks.')
		login_err = self._run_on_all_drivers(task)
		dead_sportsbooks = [sportbook.name for sportbook, err in login_err.items() if err == True]
		for dead_sportsbook in dead_sportsbooks:
			self.drop_sportsbook(dead_sportsbook)

	def	_find_polarizing_odds(self, odds):
		events = {}
		for odds in odds:
			sportsbook = odds['sportsbook']
			t1_name, t2_name = odds['t1_name'], odds['t2_name']
			t1_moneyline_odds, t2_moneyline_odds = odds['t1_moneyline_odds'], odds['t2_moneyline_odds']

			if (t1_name, t2_name) not in events:
				events[t1_name, t2_name] = {
					't1_name' : t1_name,
					't2_name' : t2_name,
					't1_moneyline_odds_min' : t1_moneyline_odds,
					't1_moneyline_odds_min_sportsbook' : sportsbook,
					't1_moneyline_odds_max' : t1_moneyline_odds,
					't1_moneyline_odds_max_sportsbook' : sportsbook,
					't2_moneyline_odds_min' : t2_moneyline_odds,
					't2_moneyline_odds_min_sportsbook' : sportsbook,
					't2_moneyline_odds_max' : t2_moneyline_odds,
					't2_moneyline_odds_max_sportsbook' : sportsbook
				}
				continue

			event = events[t1_name, t2_name]
			if t1_moneyline_odds < event['t1_moneyline_odds_min']:
				event['t1_moneyline_odds_min'] = t1_moneyline_odds
				event['t1_moneyline_odds_min_sportsbook'] = sportsbook

			if t1_moneyline_odds > event['t1_moneyline_odds_max']:
				event['t1_moneyline_odds_max'] = t1_moneyline_odds
				event['t1_moneyline_odds_max_sportsbook'] = sportsbook

			if t2_moneyline_odds < event['t2_moneyline_odds_min']:
				event['t2_moneyline_odds_min'] = t2_moneyline_odds
				event['t2_moneyline_odds_min_sportsbook'] = sportsbook

			if t2_moneyline_odds > event['t2_moneyline_odds_max']:
				event['t2_moneyline_odds_max'] = t2_moneyline_odds
				event['t2_moneyline_odds_max_sportsbook'] = sportsbook

		return events

	def _find_arbitrage(self, odds):
		events = self._find_polarizing_odds(odds)

		for (t1_name, t2_name), event in events.items():
			favorite, underdog, favorite_odds, underdog_odds = None, None, None, None
			bet_amt = 100
			if util.compute_arb(event['t1_moneyline_odds_min'], event['t2_moneyline_odds_max']) < 1:
				favorite = event['t1_name']
				underdog = event['t2_name']
				favorite_sportsbook = event['t1_moneyline_odds_min_sportsbook']
				underdog_sportsbook = event['t2_moneyline_odds_max_sportsbook']
				favorite_odds = event['t1_moneyline_odds_min']
				underdog_odds = event['t2_moneyline_odds_max']
			elif util.compute_arb(event['t1_moneyline_odds_max'], event['t2_moneyline_odds_min']) < 1:
				favorite = event['t2_name']
				underdog = event['t1_name']
				favorite_sportsbook = event['t1_moneyline_odds_max_sportsbook']
				underdog_sportsbook = event['t2_moneyline_odds_min_sportsbook']
				favorite_odds = event['t2_moneyline_odds_min']
				underdog_odds = event['t1_moneyline_odds_max']
			else:
				t1_moneyline_odds_min = event['t1_moneyline_odds_min']
				t1_moneyline_odds_min_sportsbook = event['t1_moneyline_odds_min_sportsbook']
				t1_moneyline_odds_max = event['t1_moneyline_odds_max']
				t1_moneyline_odds_max_sportsbook = event['t1_moneyline_odds_max_sportsbook']
				t2_moneyline_odds_min = event['t2_moneyline_odds_min']
				t2_moneyline_odds_min_sportsbook = event['t2_moneyline_odds_min_sportsbook']
				t2_moneyline_odds_max = event['t2_moneyline_odds_max']
				t2_moneyline_odds_max_sportsbook = event['t2_moneyline_odds_max_sportsbook']

				logger.log(
        			f'Arbitrage not found. Best odds on {t1_name} are {t1_moneyline_odds_min:.2f} ({t1_moneyline_odds_min_sportsbook}) '
               		f'and {t1_moneyline_odds_max:.2f} ({t1_moneyline_odds_max_sportsbook}).'
               	)
				logger.log(
        			f'Best odds on {t2_name} are {t2_moneyline_odds_min:.2f} ({t2_moneyline_odds_min_sportsbook}) '
					f'and {t2_moneyline_odds_max:.2f} ({t2_moneyline_odds_max_sportsbook}).'
           		)
				continue

			favorite_stake = bet_amt / ((favorite_odds/underdog_odds) + 1 )
			underdog_stake = (bet_amt*favorite_odds) / (favorite_odds + underdog_odds)
			logger.log(f'Arbitrage found! Bet {favorite_stake:.2f} on {favorite} through {favorite_sportsbook} and ')
			logger.log(f'{underdog_stake:.2f} on {underdog} through {underdog_sportsbook}.')
			logger.log(f'underdog_stake = ({bet_amt}*{favorite_odds:.2f}) / ({favorite_odds:.2f} + {underdog_odds:.2f})')
			logger.log(f'favorite_stake = {bet_amt} / (({favorite_odds:.2f}/{underdog_odds:.2f}) + 1 )')

	def bet(self):
		idx = 0
		def task(d: driver):
			return d.get_odds()

		logger.log('Entering arbitrage monitoring loop.')
		while True:
			logger.log(f'Loop {idx}.')
			results = self._run_on_all_drivers(task)
			self._find_arbitrage(list(chain.from_iterable(results.values())))
			idx += 1

	def epilogue(self):
		for sportsbook in self.drivers.values():
			sportsbook.driver_quit()