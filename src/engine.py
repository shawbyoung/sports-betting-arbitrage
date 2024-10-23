'''
This engine supports the following sportsbooks:
	- draftkings
The following betting sports/betting categories:  
	- NFL
The following kinds of bets:
	- head to head
And seeks to bet on purely pure arbitrage.
'''


class const:
	def books() -> list[str]:
		return [
			"draftkings"
		]

class Pure_Arbitrage_Engine:
	def __init__(self):
		pass

	def initialize_engine(self) -> None:
		# initialize current balances across accounts to measure when to stop betting.
		# opens windows in selenium
		pass

	def can_continue_betting(self) -> None:
		# some criteria for
		pass

	def get_bet_data(self) -> None:
		# 
		pass

	def run(self):
		pass
		# while (self.can_continue_betting()):
		# 	bet_data =


	
