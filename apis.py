# Right now the draftkings api just get nfl odds, lets push to mvp quickly. 
import json
import requests
from bs4 import BeautifulSoup
from logger import logger
# from sportsbook_api import sportsbook_api
# TODO: move 'get page functionality' into superclass. 

def convert_odds_to_decimal(american_odds: int) -> float:
    return (american_odds / 100) + 1

class h2h:
    def __init__(self, sportsbook: str, category: str, promotion: str, team_1_name: str, team_2_name: str, team_1_odds: float, team_2_odds: float):
        self.sportsbook: str = sportsbook 
        self.category: str = category
        self.promotion: str = promotion
        self.team_1_name: str = team_1_name
        self.team_2_name: str = team_2_name
        self.team_1_odds: float = team_1_odds
        self.team_2_odds: float = team_2_odds

class draftkings:
    name = "draftkings"
    categories = {}

    def __get_base_url() -> str:
        return "https://sportsbook.draftkings.com/leagues/"

    def __get_stubbed_page(category: str, promotion: str) -> str:
        stub = open(f"stubs/{draftkings.name}-{category}-{promotion}", "r")
        return stub.read()

    def __get_live_page(category: str, promotion: str) -> str:
        response = requests.get(f"{draftkings.__get_base_url()}/{category}/{promotion}")
        
        if response.status_code != 200:
            logger.log_error("Request to draftkings failed.")
            exit(1)
        
        stub = open(f"{draftkings.name}-{category}", "w")
        # TODO: consider latency here eventually.
        stub.write(response.text)
        return response.text

    def __get_page(category: str, promotion: str) -> None:
        return draftkings.__get_live_page(category, promotion) if not __debug__ else draftkings.__get_stubbed_page(category, promotion)
    
    def __process_page(page: str) -> json:
        soup = BeautifulSoup(page, 'html.parser')
        sportsbook_tables = [row.text for row in soup.find_all('tbody', class_ = 'sportsbook-table__body')]
        print(sportsbook_tables)
        for e in sportsbook_tables:
            print(e)
        return []
        
        '''
        {
            [  
                {
                    "book": "draftkings",
                    "category" : "football",
                    "promotion" : "nfl",          
                    "t1" : {
                        "odds" : 0.70
                    },
                    "t2" : {
                        "odds" : 0.31
                    }
                },
            ]
        }
        '''
        pass
    
    
    def get_odds() -> None:
        odds = []
        for category, promotions in draftkings.categories.items():
            for promotion in promotions:
                page = draftkings.__get_page(category, promotion)
                odds += draftkings.__process_page(page)
        return odds
    
# TODO: delete below, this is for testing

# draftkings.get_odds("nfl")