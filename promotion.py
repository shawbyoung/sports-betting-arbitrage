import json
import datetime
import time
import os
import util

from itertools import chain
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Type, TypeVar, Callable
from tabulate import tabulate

from logger import logger

from odds import odds
from event import event, team
from bet_request import bet_request

# Drivers
from driver import driver
from betmgm import betmgm
from betrivers import betrivers
from draftkings import draftkings
from hardrock import hardrock
from fanduel import fanduel

# Import the web display functions
from web_display import update_odds, start as start_web_display

task_res_ty = TypeVar('task_res_ty')
task_ty = Callable[[Type[driver]], task_res_ty]
drivers_list_ty = list[Type[driver]]
driver_to_task_res_opt_ty = dict[Type[driver], task_res_ty | None]

class promotion:
	events_map_ty = dict[tuple[str,str], event]

	def __init__(self, drivers):
		# Start the Flask odds display server
		start_web_display()
		self.drivers: dict[str, Type[driver]] = drivers
		self._login_flag: bool = False
		self.config()
		self.initalize_drivers()

	def run(self):
		self.login()
		self.loop()
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

	def config_login(self, config):
		login_opt = config.get('login', None)
		if login_opt == None:
			logger.log_warning('No login specification (login=false/true).')
			exit(1)
		login_flag: bool = login_opt
		self._login_flag = login_flag

	def config(self):
		try:
			with open('.config', 'r') as file:
				config = json.load(file)
		except:
			logger.log_error('No config file.')
			exit(1)

		self.config_login(config)
		self.config_promotion(config)
		self.config_sportsbooks(config)

	def _run_on_drivers(self, task: task_ty, drivers: drivers_list_ty):
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

	def _run_on_all_drivers(self, task: task_ty):
		return self._run_on_drivers(task, self.drivers.values())

	# TODO: remove all tasks private methods and replace with lambdas.
	def _login(d: driver):
		return d.login()

	def login(self):
		if self._login_flag == False:
			logger.log('Login flag set to false. Not initiating logins.')
			return

		logger.log('Logging into sportsbooks.')
		login_success = self._run_on_all_drivers(promotion._login)
		dead_sportsbooks = [sportbook.get_name() for sportbook, success in login_success.items() if success == False]
		for dead_sportsbook in dead_sportsbooks:
			self.drop_sportsbook(dead_sportsbook)

	def	_find_polarizing_odds(self, all_odds: list[odds]):
		events: promotion.events_map_ty = {}
		for sb_odds in all_odds:
			e: event | None = events.get((sb_odds.get_t1_name(), sb_odds.get_t2_name()), None)
			if not e:
				events[sb_odds.get_t1_name(), sb_odds.get_t2_name()] = event(
					sb_odds.get_t1_name(),
					sb_odds.get_t1_odds(),
					sb_odds.get_sportsbook(),
					sb_odds.get_t2_name(),
					sb_odds.get_t2_odds(),
					sb_odds.get_sportsbook(),
				)
				continue

			if sb_odds.get_t1_odds() > e.get_t1_max():
				e.update_t1(sb_odds.get_t1_odds(), sb_odds.get_sportsbook())

			if sb_odds.get_t2_odds() > e.get_t2_max():
				e.update_t2(sb_odds.get_t2_odds(), sb_odds.get_sportsbook())

		return events

	def _find_arbitrage(self, all_odds: list[odds]) -> list[bet_request]:
		events: promotion.events_map_ty = self._find_polarizing_odds(all_odds)
		bet_amt: float = 100.0

		def log_arb_found(bet_requests: list[bet_request]):
			assert len(bet_requests) == 2, 'len(bet requests) neq 2.'
			f, u = bet_requests
			logger.log(str(f))
			logger.log(str(u))
			f_winnings, f_profit = f.get_wager() * f.get_odds(), f.get_wager() * f.get_odds() - u.get_wager() - f.get_wager()
			u_winnings, u_profit = u.get_wager() * u.get_odds(), u.get_wager() * u.get_odds() - u.get_wager() - f.get_wager()
			u_winnings = u.get_wager() * u.get_odds() - u.get_wager()
			table = [['Team', 'Odds', 'Wager', 'Winnings', 'Profit'],
					 [f.get_team(), f.get_odds(), f.get_wager(), f_winnings, f_profit],
					 [u.get_team(), u.get_odds(), u.get_wager(), u_winnings, u_profit]]
			logger.log(
				tabulate(table, headers="firstrow", tablefmt="plain")
			)

		logger.log(f'Tracking {len(events)} events.')
		header = ['T1', 'T2', 'T2 Max', 'T2 Max', 'T1 SB', 'T2 SB', 'Possible Profit']
		data = []
		most_possible_profit: float | None = None
		bet_requests: list[bet_request] = []
		for (t1_name, t2_name), e in events.items():
			possible_profit: float = util.compute_profit(e.get_t1_max(), e.get_t2_max())
			data.append([
				t1_name, t2_name, f'{e.get_t1_max():.2f}', f'{e.get_t2_max():.2f}',
				e.get_t1_sportsbook(), e.get_t2_sportsbook(), f'{possible_profit:.2f}'
			])

			if possible_profit > 0:
				if most_possible_profit == None or possible_profit > most_possible_profit:
					continue
				timestamp: str = str(datetime.datetime.now())
				favorite: team = e.get_t2() if e.get_t1_max() > e.get_t2_max() else e.get_t1()
				underdog: team = e.get_t1() if e.get_t1_max() > e.get_t2_max() else e.get_t2()

				bet_requests = [
					# Favorite.
					bet_request(
						favorite.get_sportsbook(),
						favorite.get_name(),
						favorite.get_max(),
						util.compute_favorite_wager(bet_amt, favorite.get_max(), underdog.get_max()),
						timestamp
					),
					# Underdog.
					bet_request(
						underdog.get_sportsbook(),
						underdog.get_name(),
						underdog.get_max(),
						util.compute_underdog_wager(bet_amt, favorite.get_max(), underdog.get_max()),
						timestamp
					)
				]
				log_arb_found(bet_requests)

		data = sorted(data, key=lambda row: (row[0] , row[1]))
		data.insert(0, header)
		data_str = tabulate(data, headers="firstrow", tablefmt="html")
		update_odds(data_str)
		return bet_requests

	# TODO: Implement bet hedging in case of bet failure.
	def execute_bets(self, bet_requests: list[bet_request]) -> bool:
		# Assign bet requests to drivers.
		drivers: drivers_list_ty = []
		prepare_bet: Callable[[Type[driver]], bool] = lambda d: d.prepare_bet()
		execute_bet: Callable[[Type[driver]], bool] = lambda d: d.execute_bet()

		for bet_request in bet_requests:
			d: driver = self.drivers[bet_request.get_sportsbook()]
			if d not in self.drivers:
				logger.log_error(f'Invalid bet request. {bet_request.get_sportsbook()} not in drivers.')
				return False
			d.set_active_bet_request(bet_request)
			drivers.append(d)

		# Prepare bets and verify their success.
		bet_preparation_results: dict[Type[driver], bool] = self._run_on_drivers(prepare_bet, drivers)
		for d, bet_prepared in bet_preparation_results.items():
			if bet_prepared == False:
				# TODO: impl bet_request _repr_ for pretty printing for logging.
				logger.log_error(f'Could not prepare bet on {d.get_name()}.')
				return False

		# Final execution and verification.
		bet_execution_results: dict[Type[driver], bool] = self._run_on_drivers(execute_bet, drivers)
		for d, bet_executed in bet_execution_results.items():
			if bet_executed == False:
				logger.log_error(f'Could not execute bet on {d.get_name()}.')
				return False

		return True

	def loop(self):
		get_odds: Callable[[Type[driver]], list[odds]] = lambda d: d.get_odds()
		arb_identified: int = 0
		idx: int = 0
		logger.log('Entering arbitrage monitoring loop.')

		while True:
			logger.log(f'Loop {idx}. Identified {arb_identified} arbitrage opportunities.')
			results: driver_to_task_res_opt_ty = self._run_on_all_drivers(get_odds)
			events_odds: list[odds] = []
			for driver_odds in results.values():
				if driver_odds:
					events_odds += driver_odds
			bet_requests: list[bet_request] = self._find_arbitrage(events_odds)
			if bet_requests:
				if self._login_flag == True:
					logger.log('Executing bet requests.')
					self.execute_bets(bet_requests)
					logger.log('Arbitrage opportunity executed - examine output asap.')
				arb_identified += 1
			idx += 1

	def epilogue(self):
		for sportsbook in self.drivers.values():
			sportsbook.driver_quit()