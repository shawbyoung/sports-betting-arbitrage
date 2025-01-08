from driver import *

class betmgm(driver):
	def __init__(self):		
		super().__init__('betmgm')
		self.promotions = {
			'nba'
		}

	async def _login_aux(self):
		self.driver.get('https://sports.va.betmgm.com/en/sports')

	async def _collect_nba_odds(self):
		self.driver.get('https://sports.va.betmgm.com/en/sports/basketball-7/betting/usa-9/nba-6004')
		
		WebDriverWait(self.driver, 10).until(
      		EC.presence_of_element_located((By.CLASS_NAME, 'grid-event-wrapper'))
		)
		time.sleep(1)
		events = self.driver.find_elements(By.CLASS_NAME, 'grid-event-wrapper')
		
		odds = []
		for div in events:
			info_div = div.find_element(By.CLASS_NAME, 'grid-info-wrapper')
			participants = [participant_div.text for participant_div in info_div.find_elements(By.CLASS_NAME, 'participant')] 

			if len(participants) != 2:
				logger.log_warning('MGM event dropped, participants len neq 2.')
				continue

			event_odds_div = div.find_element(By.CLASS_NAME, 'grid-group-container')
			if not event_odds_div:
				logger.log_warning('MGM event dropped, no grid container.')
				continue
			
			betting_categories_wrappers = event_odds_div.find_elements(By.CLASS_NAME, 'grid-option-group')
			if len(betting_categories_wrappers) != 3:
				logger.log_warning('MGM event dropped, # of elements in event grid neq 3.')
				continue
			
			spread = betting_categories_wrappers[0].text.split()
			over_under = betting_categories_wrappers[1].text.split()
			moneyline = betting_categories_wrappers[2].text.split()

			event_odds = {
       			'team_1_name' : participants[0], 
       			'team_2_name' : participants[1]
          	}

			if len(spread) == 4:
				event_odds['team_1_spread_odds'] = spread[1]
				event_odds['team_2_spread_odds'] = spread[3]
			else: 
				logger.log_warning(f'{participants[0]}, {participants[1]} event has no spread info.')

			if len(over_under) == 6:
				event_odds['over_under_score'] = over_under[1]
				event_odds['team_1_over_odds'] = over_under[2]
				event_odds['team_2_under_odds'] = over_under[5]
			else: 
				logger.log_warning(f'{participants[0]}, {participants[1]} event has no over/under info.')
       		
			if len(moneyline) == 2:
				event_odds['team_1_moneyline_odds'] = moneyline[0]
				event_odds['team_2_moneyline_odds'] = moneyline[1]
			else: 
				logger.log_warning(f'{participants[0]}, {participants[1]} event has no moneyline info.')
			
			odds.append(event_odds)	

		return odds