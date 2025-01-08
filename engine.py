import asyncio
from bet365 import bet365
from betmgm import betmgm
from logger import logger
from itertools import chain

class engine:
	def __init__(self):
		promotions = ['nba']
		sportsbooks = [betmgm(), bet365()]
		asyncio.run(engine.login(sportsbooks))
		asyncio.run(engine.bet(sportsbooks, promotions))
		asyncio.run(engine.epilogue(sportsbooks))

	async def login(sportsbooks):
		coros = [sportsbook.login() for sportsbook in sportsbooks]
		results = await asyncio.gather(*coros)

	async def bet(sportsbooks, promotions):
		logger.log('Finding polarizing odds.')

		def find_arbitrage(odds):
			print(odds)

		for i in range(3):
			logger.log(f'Iteration {i}.')
			coros = [sportsbook.collect_odds(promotions) for sportsbook in sportsbooks]
			odds_nested = await asyncio.gather(*coros)
			find_arbitrage(list(chain.from_iterable(odds_nested)))

	async def epilogue(sportsbooks):
		for sportsbook in sportsbooks:
			sportsbook.driver_quit()