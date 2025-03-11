
import util
'''
Represents the most polarizing odds for an event.
Implemented with eventual thread safety in mind for updating odds.
'''
# TODO: impl __slots__.
class team:
    def __init__(self, name: str, max: float, sportsbook: str):
        self._name: str = name
        self._max: float = max
        self._sportsbook: str = sportsbook

    # Setters/getters.
    def set_max(self, max: float):
        self._max = max

    def get_name(self) -> str:
        return self._name

    def set_max(self, max: float):
        self._max = max

    def get_max(self) -> float:
        return self._max

    def set_sportsbook(self, sportsbook: str):
        self._sportsbook = sportsbook

    def get_sportsbook(self) -> str:
        return self._sportsbook

class event:
    # TODO: make threadsafe.
    def __init__(self, t1_name: str, t1_max: float, t1_sportsbook: str,
                       t2_name: str, t2_max: float, t2_sportsbook: str):
        self._t1: team = team(t1_name, t1_max, t1_sportsbook)
        self._t2: team = team(t2_name, t2_max, t2_sportsbook)
        self._profit: float | None = None
        self._update_profit()

    # Team 1 getters/setters.
    def get_t1(self) -> team:
        return self._t1

    def get_t1_name(self) -> str:
        return self._t1.get_name()

    def get_t1_max(self) -> float:
        return self._t1.get_max()

    def get_t1_sportsbook(self) -> str:
        return self._t1.get_sportsbook()

    # Team 2 getters/setters.
    def get_t2(self) -> team:
        return self._t2

    def get_t2_name(self) -> str:
        return self._t2.get_name()

    def get_t2_max(self) -> float:
        return self._t2.get_max()

    def get_t2_sportsbook(self) -> str:
        return self._t2.get_sportsbook()

    # Team 1 updates.
    def update_t1(self, t1_max: float, t1_sportsbook: str):
        self._t1.set_max(t1_max)
        self._t1.set_sportsbook(t1_sportsbook)
        self._update_profit()

    # Team 2 updates.
    def update_t2(self, t2_max: float, t2_sportsbook: str):
        self._t2.set_max(t2_max)
        self._t2.set_sportsbook(t2_sportsbook)
        self._update_profit()

    # Profit functions.
    def get_profit(self) -> float | None:
        return self._profit

    def _update_profit(self) -> None:
        self._profit = util.compute_profit(self._t1.get_max(), self._t2.get_max())