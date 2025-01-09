import asyncio
import util
from hardrock import hardrock
from betmgm import betmgm
from logger import logger
from itertools import chain

class engine:
	def __init__(self):
		promotions = ['nba']
		sportsbooks = [betmgm(), hardrock()]
		asyncio.run(engine.login(sportsbooks))
		asyncio.run(engine.bet(sportsbooks, promotions))
		asyncio.run(engine.epilogue(sportsbooks))

	async def login(sportsbooks):
		coros = [sportsbook.login() for sportsbook in sportsbooks]
		results = await asyncio.gather(*coros)

	def	_find_polarizing_odds(odds):
		events = {}
		for odds in odds:
			sportsbook = odds['sportsbook']
			t1_name, t2_name = odds['t1_name'], odds['t2_name']
			t1_moneyline_odds, t2_moneyline_odds = odds['t1_moneyline_odds'], odds['t2_moneyline_odds']

			if (t1_name, t2_name) not in events:
				events[t1_name, t2_name] = {
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

	def _find_arbitrage(odds):
		events = engine._find_polarizing_odds(odds)

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
        			f'Best odds on {t2_name} are {t2_moneyline_odds_min:.2f}({t2_moneyline_odds_min_sportsbook}) '
					f'and {t2_moneyline_odds_max:.2f}({t2_moneyline_odds_max_sportsbook}).'
           		)
				continue

			favorite_stake = bet_amt / ((favorite_odds/underdog_odds) + 1 )
			underdog_stake = (bet_amt*favorite_odds) / (favorite_odds + underdog_odds)
			logger.log(f'Arbitrage found! Bet {favorite_stake:.2f} on {favorite} through {favorite_sportsbook} and ')
			logger.log(f'{underdog_stake:.2f} on {underdog} through {underdog_sportsbook}.')
			logger.log(f'underdog_stake = ({bet_amt}*{favorite_odds:.2f}) / ({favorite_odds:.2f} + {underdog_odds:.2f})')
			logger.log(f'favorite_stake = {bet_amt} / (({favorite_odds:.2f}/{underdog_odds:.2f}) + 1 )')

	async def bet(sportsbooks, promotions):
		logger.log('Entering arbitrage monitoring loop.')
		idx = 0

		while True:
			logger.log(f'Loop {idx}')
			coros = [sportsbook.collect_odds(promotions) for sportsbook in sportsbooks]
			odds_nested = await asyncio.gather(*coros)
			engine._find_arbitrage(list(chain.from_iterable(odds_nested)))
			idx += 1

	async def epilogue(sportsbooks):
		for sportsbook in sportsbooks:
			sportsbook.driver_quit()