import json
from logger import logger
import apis 

class engine:
	sportsbooks: dict[str, dict] = {}
	sportsbook_apis: list = []
	categories: dict[str, list[str]] = {}
 
	def initialize():
		logger.log(f"Initializing betting engine.")
		with open('.config', 'r') as config_file: config_text = config_file.read()
		config = json.loads(config_text)

		engine.categories = config["categories"]  
		for category in engine.categories:
			logger.log(f"Betting on {category} with promotions {engine.categories[category]}")   			

		engine.sportsbooks = config["sportsbooks"]
		engine.initialize_sportsbook_apis()
		logger.log(f"Betting on the following sportsbooks: {list(engine.sportsbooks.keys())}")		
	
	def initialize_sportsbook_apis() -> None:
		engine.sportsbook_apis = [getattr(apis, sportsbook) for sportsbook in engine.sportsbooks.keys()]
		for api in engine.sportsbook_apis:
			api.categories = engine.categories
    	# initialize current balances across accounts to measure when to stop betting.
		# opens windows in selenium

	def can_continue_betting() -> None:
		# some criteria for
		pass

	def get_bet_data() -> None:
		# 
		pass

	def request_odds():
		for sportsbook in engine.books:
			sportsbook_api = getattr(apis, sportsbook)
			result = sportsbook_api()

	def get_odds_from_all_sportsbooks():
		# TODO: Make async
		odds = []
		for sportsbook_api in engine.sportsbook_apis:
			odds += sportsbook_api.get_odds()
		# TODO: dynamically check odds for bet opportunities, refresh odds when bet is found and executed.
		# will need to check the above for actual wins, GET WORKING FIRST
		return odds

	def run():
		odds = engine.get_odds_from_all_sportsbooks()
				

	# def get_most_polarizing_odds(team_1):
    #  	pass