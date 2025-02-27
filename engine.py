import json
import time
import os
import util

from itertools import chain
from concurrent.futures import ThreadPoolExecutor, as_completed

from driver import driver
from logger import logger
from odds import odds
from event import event
from bet_request import bet_request

# Drivers
from betmgm import betmgm
from betrivers import betrivers
from draftkings import draftkings 
from hardrock import hardrock
from fanduel import fanduel

class engine:
	events_map_ty = dict[tuple[str,str], event]

	def __init__(self, drivers):
		self.drivers = drivers
		self.config()
		self.initalize_drivers()

	def run(self):
		self.login()
		self.bet()
		self.epilogue()

	def initalize_drivers(self):
		for d in self.drivers.values():
			d.initialize_webdriver()

	def drop_sportsbook(self, sportsbook):
		if sportsbook not in self.drivers:
			logger.log(f'{sportsbook} not in drivers, unable to drop.')
			return

		self.drivers[sportsbook].driver_quit()
		del self.drivers[sportsbook]
		logger.log(f'Dropping sportbook {sportsbook}')

	def config_promotion(self, config):
		promotion_opt = config.get('promotion', None) 
		if not promotion_opt:
			logger.log_error('No promotion in config file.')
			exit(1)

		util.promotion = promotion_opt
		logger.log(f'{util.promotion} selected as promotion.')

	def config_sportsbooks(self, config):
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
				logger.log_warning(f'{sportsbook} in .config but not initialized.')
				continue

			if not username:
				logger.log_error(f'No username in {sportsbook} config .')
				exit(1)

			if not password:
				logger.log_error(f'No password in {sportsbook} config .')
				exit(1)

			self.drivers[sportsbook].set_username(username)
			self.drivers[sportsbook].set_password(password)

		self.set_profiles(config)

	def set_profiles(self, config):
		profiles_directory = config.get('profiles_directory', None)
		profiles = config.get('profiles', None)

		if not profiles_directory:
			logger.log_error('\'profiles_directory\' undefined in .config.')
			exit(1)

		if not profiles:
			logger.log_error('\'profiles\' undefined in .config.')
			exit(1)

		for profile, driver in zip(profiles, self.drivers.values()):
			driver.set_user_data_dir(profiles_directory + profile)

	def config(self):
		try:
			with open('.config', 'r') as file:
				config = json.load(file)
		except:
			logger.log_error('No config file.')
			exit(1)

		self.config_promotion(config)
		self.config_sportsbooks(config)

	def _run_on_drivers(self, task, drivers):
		results = {}
		if len(drivers) == 0:
			logger.log_error('No drivers.')
			return results

		with ThreadPoolExecutor(max_workers=len(drivers)) as executor:
			future_to_driver = {executor.submit(task, d): d for d in drivers}
			for future in as_completed(future_to_driver):
				driver_obj = future_to_driver[future]
				try:
					results[driver_obj] = future.result()
				except Exception as e:
					logger.log_error(f"Error with driver {driver_obj}: {e}")
					# TODO: Change `results[driver_obj]` back to None and add smth to handle that in
					# bet so that _run_on_all_drivers returns output that's handle-able by a multitude of tasks.
					results[driver_obj] = None

		return results

	def _run_on_all_drivers(self, task):
		return self._run_on_drivers(task, self.drivers.values())

	def _login(d: driver):
		return d.login()

	def login(self):
		logger.log('Logging into sportsbooks.')
		login_success = self._run_on_all_drivers(engine._login)
		dead_sportsbooks = [sportbook.get_name() for sportbook, success in login_success.items() if success == False]
		for dead_sportsbook in dead_sportsbooks:
			self.drop_sportsbook(dead_sportsbook)

	def	_find_polarizing_odds(self, all_odds: list[odds]):
		events: engine.events_map_ty = {}
		for sb_odds in all_odds:
			e: event | None = events.get((sb_odds.get_t1_name(), sb_odds.get_t2_name()), None)
			if not e:
				events[sb_odds.get_t1_name(), sb_odds.get_t2_name()] = event(
					sb_odds.get_t1_name(),
					sb_odds.get_t2_name(),
					sb_odds.get_t1_odds(),
					sb_odds.get_sportsbook(),
					sb_odds.get_t1_odds(),
					sb_odds.get_sportsbook(),
					sb_odds.get_t2_odds(),
					sb_odds.get_sportsbook(),
					sb_odds.get_t2_odds(),
					sb_odds.get_sportsbook(),
				)
				continue

			if sb_odds.get_t1_odds() < e.get_t1_min():
				e.update_t1_min(sb_odds.get_t1_odds(), sb_odds.get_sportsbook())

			if sb_odds.get_t1_odds() > e.get_t1_max():
				e.update_t1_max(sb_odds.get_t1_odds(), sb_odds.get_sportsbook())

			if sb_odds.get_t2_odds() < e.get_t2_min():
				e.update_t2_min(sb_odds.get_t2_odds(), sb_odds.get_sportsbook())

			if sb_odds.get_t2_odds() > e.get_t2_max():
				e.update_t2_max(sb_odds.get_t2_odds(), sb_odds.get_sportsbook())

		return events

	def _find_arbitrage(self, all_odds: list[odds]) -> list[bet_request]:
		events: engine.events_map_ty = self._find_polarizing_odds(all_odds)
		bet_amt: float = 100.0

		def log_arb_found(bet_request: list[bet_request]):
			assert len(bet_request) == 2, 'len(bet requests) neq 2.'
			f, u = bet_request
			logger.log(
				f'Arbitrage found! Bet {f.get_wager()} on {f.get_team()} through {f.get_sportsbook()} and '
				f'{u.get_wager()} on {u.get_team()} through {u.get_sportsbook()}.'
			)
			logger.log(
				f'Favorite wager = {bet_amt} / (({f.get_odds():.2f}/{u.get_odds():.2f}) + 1 ) ~= {f.get_wager()}.'
			)
			logger.log(
				f'Underdog wager = ({bet_amt}*{f.get_odds():.2f}) / ({f.get_odds():.2f} + {u.get_odds():.2f}) ~= {u.get_wager()}.'
			)
			logger.log(
				f'Profit = {util.compute_winnings(f.get_wager(), f.get_odds(), u.get_wager(), u.get_odds())}'
			)

		for (t1_name, t2_name), e in events.items():
			if util.compute_profit(e.get_t1_min(), e.get_t2_max()) > 1:
				bet_requests = [
					# Favorite.
					bet_request(
						e.get_t1_min_sportsbook(),
						e.get_t1_name(),
						e.get_t1_min(),
						util.compute_favorite_wager(bet_amt, e.get_t1_min(), e.get_t2_max)
					),
					# Underdog.
					bet_request(
						e.get_t2_max_sportsbook(),
						e.get_t2_name(),
						e.get_t2_max(),
						util.compute_underdog_wager(bet_amt, e.get_t1_min(), e.get_t2_max)
					)
				]
				log_arb_found(bet_requests)
			if util.compute_profit(e.get_t1_max(), e.get_t2_min()) > 1:
				bet_requests = [
					# Favorite.
					bet_request(
						e.get_t2_min_sportsbook(),
						e.get_t2_name(),
						e.get_t2_min(),
						util.compute_favorite_wager(bet_amt, e.get_t2_min(), e.get_t1_max)
					),
					# Underdog.
					bet_request(
						e.get_t1_max_sportsbook(),
						e.get_t1_name(),
						e.get_t1_max(),
						util.compute_underdog_wager(bet_amt, e.get_t2_min(), e.get_t1_max)
					)
				]
				log_arb_found(bet_requests)

			logger.log(
				f'Arbitrage not found. Best odds on {t1_name} are {e.get_t1_min():.2f} ({e.get_t1_min_sportsbook()}) '
				f'and {e.get_t1_max():.2f} ({e.get_t1_max_sportsbook()}).'
			)
			logger.log(
				f'Best odds on {t2_name} are {e.get_t2_min():.2f} ({e.get_t2_min_sportsbook()}) '
				f'and {e.get_t2_max():.2f} ({e.get_t2_max_sportsbook()}).'
			)


		return None

	def _get_odds(d: driver):
		return d.get_odds()

	def _execute_bet(d: driver):
		return d.execute_bet()

	def execute_bets(self, bet_requests: list[bet_request]):
		# Assign bet requests to drivers.
		drivers = []
		for bet_request in bet_requests:
			if bet_request.get_sportsbook() not in self.drivers:
				logger.log_error(f'Invalid bet request. {bet_request.get_sportsbook()} not in drivers.')
				continue
			driver = self.drivers[bet_request.get_sportsbook()]
			driver.set_active_bet_request(bet_request)
			drivers.append(driver)
		self._run_on_drivers(engine._execute_bet, drivers)

	def bet(self):
		idx = 0
		logger.log('Entering arbitrage monitoring loop.')
		while True:
			logger.log(f'Loop {idx}.')
			results = self._run_on_all_drivers(engine._get_odds)
			odds = []
			for driver_odds in results.values():
				if driver_odds:
					odds += driver_odds
			bet_requests = self._find_arbitrage(odds)
			if bet_requests:
				self.execute_bets(bet_requests)
			idx += 1

	def epilogue(self):
		for sportsbook in self.drivers.values():
			sportsbook.driver_quit()