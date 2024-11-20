'''
This engine supports the following sportsbooks:
	- draftkings
The following betting sports/betting categories:  
	- NFL
The following kinds of bets:
	- head to head
And seeks to bet on purely pure arbitrage.
'''
from sportsbook_apis import *
import sportsbook_apis
import json

class engine:
	def __init__(self):
  		# reads .config file to login and shit.
		with open('.config', 'r') as config_file: config_text = config_file.read()
		config = json.loads(config_text)
		self.books: list[str] = config["books"]
		self.categories: list[str] = config["categories"]
		# initialize current balances across accounts to measure when to stop betting.
		# opens windows in selenium

	def can_continue_betting(self) -> None:
		# some criteria for
		pass

	def get_bet_data(self) -> None:
		# 
		pass

	def request_odds(self):
		for sportsbook in self.books:
			# Given a module foo with method bar:
			bar = getattr(sportsbook_apis, 'bar')
			result = bar()

	def run(self):
		# while (self.can_continue_betting()):
		sportbook_odds = self.request
		pass
		

	# def get_most_polarizing_odds(team_1):
    #  	pass