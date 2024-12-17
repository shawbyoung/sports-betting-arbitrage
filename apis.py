# Right now the draftkings api just get nfl odds, lets push to mvp quickly. 
import json
import requests
from bs4 import BeautifulSoup
from logger import logger
# from sportsbook_api import sportsbook_api
# TODO: move 'get page functionality' into superclass. 

'''
> football
> nfl
> moneyline ?
'''

def convert_odds_to_decimal(american_odds: int) -> float:
    return (american_odds / 100) + 1

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

class api:
    pass
    # name = ""
    # categories = {}
    
    # def __get_stubbed_page(category: str, promotion: str) -> str:
    #     stub = open(f"stubs/{api.name}-{category}-{promotion}", "r")
    #     return stub.read()
    
    # def __get_live_page(category: str, promotion: str) -> str:
    #     response = requests.get(f"{draftkings.__get_base_url()}/{category}/{promotion}")
        
    #     if response.status_code != 200:
    #         logger.log_error("Request to draftkings failed.")
    #         exit(1)
        
    #     stub = open(f"{draftkings.name}-{category}", "w")
    #     # TODO: consider latency here eventually.
    #     stub.write(response.text)
    #     return response.text

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
    
    def __get_team_information(team):
        team_name_div = team.find("th", class_ = "sportsbook-table__column-row").find("div", class_ = "event-cell__name-text")
        team_name = team_name_div.get_text()                
        '''
        odds[0] corresponds to spread.
        odds[1] corresponds to total.
        '''
        odds = team.find_all("td", class_ = "sportsbook-table__column-row")
        assert len(odds) == 3, "Draftkings has three markets: spread, total, and moneyline." 

        moneyline_odds_div = odds[2].find("span", class_ = "sportsbook-odds")
        moneyline_odds_text = moneyline_odds_div.get_text()

        return team_name, convert_odds_to_decimal(int(moneyline_odds_text[1:]))

    def __get_game_odds(team_1, team_2):
        team_1_name, team_1_moneyline_odds = draftkings.__get_team_information(team_1)
        team_2_name, team_2_moneyline_odds = draftkings.__get_team_information(team_2)
        
        return {
            "team_1_name" : team_1_name, 
            "team_2_name" : team_2_name,
            "team_1_moneyline_odds" : team_1_moneyline_odds,
            "team_2_moneyline_odds" : team_2_moneyline_odds
        }
    
    def __process_page(page: str) -> json:
        soup = BeautifulSoup(page, 'html.parser')
        sportsbook_tables = soup.find_all('tbody', class_ = 'sportsbook-table__body')

        if not sportsbook_tables:
            return []

        # Game odds are two tr elements separated by breaklines
        for sportsbook_table in sportsbook_tables:
            rows = sportsbook_table.find_all("tr", recursive=False)
            games = []
            n_rows = len(rows)

            # You're given pairs
            for i in range(0, n_rows, 2):
                games.append((rows[i], rows[i+1]))

            for team_1, team_2 in games:
                game_odds = draftkings.__get_game_odds(team_1, team_2)
                print(game_odds, '\n')
                            
        return []
    
    def get_odds() -> None:
        odds = []
        for category, promotions in draftkings.categories.items():
            for promotion in promotions:
                page = draftkings.__get_page(category, promotion)
                odds += draftkings.__process_page(page)
        return odds

# TODO: delete below, this is for testing

# draftkings.get_odds("nfl")