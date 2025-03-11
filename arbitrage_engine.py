import datetime
import util

from typing import Type, Callable

from bet_request import bet_request
from driver import driver, drivers
from event import event, team
from event_table import event_table
from logger import logger
from odds import odds
from perform_arbitrage_arr import perform_arbitrage_err
from tabulate import tabulate
from web_display import update_odds

class arbitrage_engine:
	def __init__(self, drivers_: drivers.stringmap):
		self._login_flag: bool = False
		self._mock_flag: bool = True
		self._drivers: drivers.stringmap = drivers_

	def set_login_flag(self, flag: bool):
		self._login_flag = flag

	def login_flag(self) -> bool:
		return self._login_flag

	def set_mock_flag(self, flag: bool):
		self._mock_flag = flag

	def mock_flag(self) -> bool:
		return self._mock_flag

	def _get_drivers(self) -> list[driver]:
		return self._drivers.values()

	def drop_sportsbook(self, sportsbook):
		if sportsbook not in self.drivers:
			logger.log(f'{sportsbook} not in drivers, unable to drop.')
			return

		self.drivers[sportsbook].driver_quit()
		del self.drivers[sportsbook]
		logger.log(f'Dropping sportbook {sportsbook}')

	def login(self):
		if self._login_flag == False:
			logger.log('Login flag set to false. Not initiating logins.')
			return

		logger.log('Logging into sportsbooks.')
		login: Callable[[Type[driver]], bool] = lambda d: d.login()
		login_success = drivers.run_on_drivers(login, self._get_drivers())
		dead_sportsbooks = [sportbook.get_name() for sportbook, success in login_success.items() if success == False]
		for dead_sportsbook in dead_sportsbooks:
			self.drop_sportsbook(dead_sportsbook)

	def	_find_polarizing_odds(self, all_odds: list[odds]):
		events: event_table = {}
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

	def identify_arbitrage(self, all_odds: list[odds]) -> list[bet_request]:
		events: event_table = self._find_polarizing_odds(all_odds)
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
		loose_drivers: list[driver] = []
		prepare_bet: Callable[[Type[driver]], bool] = lambda d: d.prepare_bet()
		execute_bet: Callable[[Type[driver]], bool] = lambda d: d.execute_bet((not self.login_flag()) | self.mock_flag())

		for bet_request in bet_requests:
			sportsbook: str = bet_request.get_sportsbook()
			if sportsbook not in self._drivers:
				logger.log_error(f'Invalid bet request. {sportsbook} not in drivers.')
				for d in loose_drivers:
					d.set_active_bet_request(None)
				return False
			d: str = self.drivers[sportsbook]
			d.set_active_bet_request(bet_request)
			loose_drivers.append(d)

		# Prepare bets and verify their success.
		bet_preparation_results: dict[Type[driver], bool] = drivers.run_on_drivers(prepare_bet, loose_drivers)
		for d, bet_prepared in bet_preparation_results.items():
			if bet_prepared == False:
				# TODO: impl bet_request _repr_ for pretty printing for logging.
				logger.log_error(f'Could not prepare bet on {d.get_name()}.')
				return False

		# Final execution and verification.
		# TODO: implement bet hedging in case of bet failure + program termination after a certain number of failed bets
		# as well as clearing active bet requests.
		bet_execution_results: dict[Type[driver], bool] = drivers.run_on_drivers(execute_bet, loose_drivers)
		for d, bet_executed in bet_execution_results.items():
			if bet_executed == False:
				logger.log_error(f'Could not execute bet on {d.get_name()}.')
				return False

		for d in loose_drivers:
			d.set_active_bet_request(None)
		return True

	def perform_arbitrage(self, event_odds: list[odds]) -> perform_arbitrage_err:
		bet_requests: list[bet_request] = self.identify_arbitrage(event_odds)
		if not bet_requests:
			return perform_arbitrage_err(False, False)
		return perform_arbitrage_err(True, self.execute_bets(bet_requests))