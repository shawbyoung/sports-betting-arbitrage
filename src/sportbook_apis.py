import requests
from logger import logger
# right now the draftkings api just get nfl odds, lets push to mvp quickly. 

class draftkings:
    # tested with just nfl for now
    def get_odds(category: str):
        response = requests.get(f"https://sportsbook.draftkings.com/leagues/football/{category}")
        
        if response.status_code != 200:
            logger.log_error("Initial request to draftkings failed.")
            exit(1)

        f = open(f"draftkings{category}", "w")
        f.write(response.text)
        f.close()

# TODO: delete below, this is for testing

# draftkings.get_odds("nfl")