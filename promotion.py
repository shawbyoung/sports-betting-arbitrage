import json
import util

from typing import Type, Callable

from arbitrage_engine import arbitrage_engine
from driver import driver, drivers
from logger import logger
from odds import odds
from perform_arbitrage_arr import perform_arbitrage_err
from web_display import start as start_web_display

class promotion:
	def __init__(self, drivers):
		# Start the Flask odds display server
		start_web_display()
		self.drivers: dict[str, Type[driver]] = drivers
		self._arbitrage_engine: arbitrage_engine = arbitrage_engine(self.drivers)
		self.config()
		self.initalize_drivers()

	def _get_drivers(self) -> list[Type[driver]]:
		return list(self.drivers.values())

	def run(self):
		self._arbitrage_engine.login()
		self.loop()
		self.epilogue()

	def initalize_drivers(self):
		for d in self._get_drivers():
			d.initialize_webdriver()

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

		for profile, driver in zip(profiles, self._get_drivers()):
			driver.set_user_data_dir(profiles_directory + profile)

	def config_login(self, config):
		login_opt = config.get('login', None)
		if login_opt == None:
			logger.log_warning('No login specification (login=false/true).')
			exit(1)
		login_flag: bool = login_opt
		self._arbitrage_engine.set_login_flag(login_flag)

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

	def loop(self):
		get_odds: Callable[[Type[driver]], list[odds]] = lambda d: d.get_odds()
		arb_identified: int = 0
		idx: int = 0
		logger.log('Entering arbitrage monitoring loop.')

		while True:
			logger.log(f'Loop {idx}. Identified {arb_identified} arbitrage opportunities.')
			results: dict[Type[driver], list[odds]] = drivers.run_on_drivers(get_odds, self._get_drivers())
			events_odds: list[odds] = []
			for driver_odds in results.values():
				if driver_odds:
					events_odds.extend(driver_odds)
			err: perform_arbitrage_err = self._arbitrage_engine.perform_arbitrage(events_odds)
			if err.arb_identified():
				logger.log('Arbitrage opportunity identified.')
				arb_identified += 1
			if err.executed():
				logger.log('Arbitrage opportunity executed - examine output ASAP.')
			idx += 1

	def epilogue(self):
		for sportsbook in self._get_drivers():
			sportsbook.driver_quit()