# Right now the draftkings api just get nfl odds, lets push to mvp quickly. 
import json
import requests
import util

from bs4 import BeautifulSoup
from logger import logger

class api:
    def __init__(self, name: str, categories):
        self.name = name
        self.categories = categories
    
    # Subclasses must implement.
    def _get_base_url(self):
        return ""
    
    def _get_stubbed_page(self, category: str, promotion: str) -> str:
        stub = open(f"stubs/{self.name}-{category}-{promotion}", "r")
        return stub.read()
    
    def _url_disambiguator(self, category: str, promotion: str) -> str:
        return ""
        
    def _get_live_page(self, category: str, promotion: str) -> str:
        url = self._url_disambiguator(category, promotion)
        logger.log(f"Requesting {self.name} for {category}/{promotion}.")
        response = requests.get(url)
        
        if response.status_code != 200:
            logger.log_error(f"Request to {self.name} failed. Tried {url}")
            exit(1)

        stub = open(f"stubs/{self.name}-{category}-{promotion}", "w")
        # TODO: consider latency here eventually. perhaps add a setting in config
        # that turns on writing to file and make async.
        stub.write(response.text)
        return response.text

    def _get_page(self, category: str, promotion: str) -> None:
        return self._get_live_page(category, promotion) if not __debug__ else self._get_stubbed_page(category, promotion)

    # Subclasses must implement.
    def _process_page(self, page: str) -> json:                            
        return []
    
    def get_odds(self) -> None:
        odds = []
        for category, promotions in self.categories.items():
            for promotion in promotions:
                page = self._get_page(category, promotion)
                odds += self._process_page(page)
        return odds

class draftkings(api):
    def __init__(self, categories):
        super().__init__("draftkings", categories)

    def _get_base_url(self) -> str:
        return "https://sportsbook.draftkings.com/leagues/"

    def _get_stubbed_page(self, category: str, promotion: str) -> str:
        return super()._get_stubbed_page(category, promotion)

    def _url_disambiguator(self, category: str, promotion: str) -> str:
        return f"{self._get_base_url()}/{category}/{promotion}"

    def _get_live_page(self, category: str, promotion: str) -> str:
        return super()._get_live_page(category, promotion)

    def _get_page(self, category: str, promotion: str) -> None:
        return super()._get_page(category, promotion)
    
    def _get_team_information(self, team):
        team_name_div = team.find("th", class_ = "sportsbook-table__column-row").find("div", class_ = "event-cell__name-text")
        team_name = team_name_div.get_text()                
        '''`
        odds[0] corresponds to spread.
        odds[1] corresponds to total.
        '''
        odds = team.find_all("td", class_ = "sportsbook-table__column-row")
        assert len(odds) == 3, "Draftkings has three markets: spread, total, and moneyline." 

        moneyline_odds_div = odds[2].find("span", class_ = "sportsbook-odds")
        moneyline_odds_text = moneyline_odds_div.get_text()

        return team_name, util.convert_odds_to_decimal(int(moneyline_odds_text[1:]))

    def _get_game_odds(self, team_1, team_2):
        team_1_name, team_1_moneyline_odds = self._get_team_information(team_1)
        team_2_name, team_2_moneyline_odds = self._get_team_information(team_2)
        
        return {
            "team_1_name" : team_1_name, 
            "team_2_name" : team_2_name,
            "team_1_moneyline_odds" : team_1_moneyline_odds,
            "team_2_moneyline_odds" : team_2_moneyline_odds
        }
    
    def _process_page(self, page: str) -> json:
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
                game_odds = self._get_game_odds(team_1, team_2)
                print(game_odds, '\n')
                            
        return []
    
    def get_odds(self) -> None:
        return super().get_odds()

class betrivers(api):
    def __init__(self, categories):
        super().__init__("betrivers", categories)

    def _get_base_url(self) -> str:
        return "https://va.betrivers.com/"

    def _get_stubbed_page(self, category: str, promotion: str) -> str:
        return super()._get_stubbed_page(category, promotion)

    def _url_disambiguator(self, category: str, promotion: str):
        match category:
            case "football":
                match promotion:
                    case "nfl":
                        # Try to make sense of the urls later if/when we expand
                        return f"{self._get_base_url()}?page=sportsbook&group=1000093656&type=matches#home"
                    case _:
                        return ""
            case _:
                return ""
                            
    def _get_live_page(self, category: str, promotion: str) -> str:
        return super()._get_live_page(category, promotion)

    def _get_page(self, category: str, promotion: str) -> None:
        return super()._get_page(category, promotion)
    
    def _get_team_information(self, team):
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

        return team_name, util.convert_odds_to_decimal(int(moneyline_odds_text[1:]))

    def _get_game_odds(self, team_1, team_2):
        team_1_name, team_1_moneyline_odds = self._get_team_information(team_1)
        team_2_name, team_2_moneyline_odds = self._get_team_information(team_2)
        
        return {
            "team_1_name" : team_1_name, 
            "team_2_name" : team_2_name,
            "team_1_moneyline_odds" : team_1_moneyline_odds,
            "team_2_moneyline_odds" : team_2_moneyline_odds
        }
    
    def _process_page(self, page: str) -> json:
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
                game_odds = self._get_game_odds(team_1, team_2)
                print(game_odds, '\n')
                            
        return []
    
    def get_odds(self) -> None:
        return super().get_odds()