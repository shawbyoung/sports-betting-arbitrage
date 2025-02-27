'''
Represents a bet request, immutable.
'''
class bet_request:
    def __init__(self, sportsbook: str, team: str, odds: float, wager: int):
        self._sportsbook: str = sportsbook
        self._team: str = team
        self._odds: float = odds
        self._wager: int = wager

    def get_sportsbook(self) -> str:
        return self._sportsbook

    def get_team(self) -> str:
        return self._team

    def get_odds(self) -> float:
        return self._odds

    def get_wager(self) -> int:
        return self._wager