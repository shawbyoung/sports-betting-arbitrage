# Right now the draftkings api just get nfl odds, lets push to mvp quickly. 
import requests
from src.logger import logger
from src.sportsbook_odds import sportsbook_odds
# from sportsbook_api import sportsbook_api

# TODO: move 'get page functionality' into superclass. 

class draftkings_api:
    name = "draftkings"

    def __get_base_url() -> str:
        return "https://sportsbook.draftkings.com/leagues/"

    def __get_stubbed_page(category: str, promotion: str) -> str:
        stub = open(f"stubs/{draftkings_api.name}-{category}-{promotion}", "r")
        return stub.readlines()

    def __get_live_page(category: str, promotion: str) -> str:
        response = requests.get(f"{draftkings_api.__get_base_url()}/{category}/{promotion}")
        
        if response.status_code != 200:
            logger.log_error("Initial request to draftkings failed.")
            exit(1)
        
        stub = open(f"{draftkings_api.name}-{category}", "w")
        # TODO: consider latency here eventually.
        stub.write(response.text)
        return response.text

    def __get_page(category: str, promotion: str) -> None:
        return draftkings_api.__get_live_page(category, promotion) if not __debug__ else draftkings_api.__get_stubbed_page(category, promotion)
    
    def __process_page(page: str) -> json:
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
    
    def get_odds(category: str, promotion: str) -> None:
        page = draftkings_api.__get_page(category, promotion)
        return draftkings_api.__process_page(page)
    
# TODO: delete below, this is for testing

# draftkings.get_odds("nfl")