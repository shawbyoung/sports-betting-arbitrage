from driver import *

class bet365(driver):
	def __init__(self):
		super().__init__('bet365')
		self.promotions = {
			'nba'
		}
  	
	async def _login_aux(self):
		self.driver.get('https://www.va.bet365.com/?_h=k4xguHn5G-8CfnOdS7-WMQ%3D%3D&btsffd=1#/HO/')

	async def _collect_nba_odds(self):
		return [{'dud' : 'dud'}]