'''
Represents a bet request, immutable.
'''
class bet_request:
    def __init__(self, sportsbook: str, team: str, odds: float, wager: int,  time_stamp: str):
        self._sportsbook: str = sportsbook
        self._team: str = team
        self._odds: float = odds
        self._wager: int = wager
        self._time_stamp: str = time_stamp

    def get_sportsbook(self) -> str:
        return self._sportsbook

    def get_team(self) -> str:
        return self._team

    def get_odds(self) -> float:
        return self._odds

    def get_wager(self) -> int:
        return self._wager

    def get_time_stamp(self) -> str:
        return self._time_stamp

    def __repr__(self) -> str:
        return (f'bet_request('
                    f'sportsbook={self._sportsbook}, ' 
                    f'team={self._team}, '
                    f'odds={self._odds}, '
                    f'wager={self._wager}, '
                    f'time_stamp={self._time_stamp})'
                    f'')