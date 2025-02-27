import util
from logger import logger
from typing import Callable

'''
Represents the moneyline odds for an event, immutable.
'''
class odds:
    def construct_odds(sportsbook: str, participants: list[str], moneyline: list[str]):
        if len(participants) != 2:
            logger.log_warning(f'len(participants) != 2. {participants}.')
            return None

        if len(moneyline) != 2:
            logger.log_warning(f'[{sportsbook}] event has invalid moneyline info {moneyline}, dropping.')
            return None

        for odd in moneyline:
            if not odd[1:].isnumeric():
                logger.log_warning(f'[{sportsbook}] event has invalid moneyline info {moneyline}, dropping.')
                return None

        return odds(sportsbook, participants, moneyline)

    def __init__(self, sportsbook: str, participants: list[str], moneyline: list[str]):
        if participants[0] < participants[1]:
            t1_participants_idx = 0
            t2_participants_idx = 1
            t1_moneyline_idx = 0
            t2_moneyline_idx = 1
        else:
            t1_participants_idx = 1
            t2_participants_idx = 0
            t1_moneyline_idx = 1
            t2_moneyline_idx = 0

        self._sportsbook: str = sportsbook
        self._t1_name: str = participants[t1_participants_idx]
        self._t2_name: str = participants[t2_participants_idx]
        self._t1_odds: float = util.american.to_decimal(moneyline[t1_moneyline_idx])
        self._t2_odds: float = util.american.to_decimal(moneyline[t2_moneyline_idx])

    def get_sportsbook(self) -> str:
        return self._sportsbook

    def get_t1_name(self) -> str:
        return self._t1_name

    def get_t2_name(self) -> str:
        return self._t2_name

    def get_t1_odds(self) -> str:
        return self._t1_odds

    def get_t2_odds(self) -> str:
        return self._t2_odds