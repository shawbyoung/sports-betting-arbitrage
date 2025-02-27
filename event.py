
'''
Represents the most polarizing odds for an event.
Implemented with eventual thread safety in mind for updating odds.
'''
class event:
    # TODO: make threadsafe.
    def __init__(self, t1_name: str, t2_name: str, 
                t1_min: float, t1_min_sportsbook: str, t1_max: float, t1_max_sportsbook: str,
                t2_min: float, t2_min_sportsbook: str, t2_max: float, t2_max_sportsbook: str):
        self._t1_name: str = t1_name
        self._t2_name: str = t2_name
        self._t1_min: float = t1_min
        self._t1_min_sportsbook: str = t1_min_sportsbook
        self._t1_max: float = t1_max
        self._t1_max_sportsbook: str = t1_max_sportsbook
        self._t2_min: float = t2_min
        self._t2_min_sportsbook: str = t2_min_sportsbook
        self._t2_max: float = t2_max
        self._t2_max_sportsbook: str = t2_max_sportsbook

    # Team 1 getters/setters.
    def get_t1_name(self) -> str:
        return self._t1_name

    def get_t1_min(self) -> float:
        return self._t1_min

    def _set_t1_min(self, t1_min: float):
        self._t1_min = t1_min

    def get_t1_max(self) -> float:
        return self._t1_max

    def _set_t1_max(self, t1_max: float):
        self._t1_max = t1_max

    def get_t1_min_sportsbook(self):
        return self._t1_min_sportsbook

    def _set_t1_min_sportsbook(self, t1_min_sportsbook: str):
        self._t1_min_sportsbook = t1_min_sportsbook

    def get_t1_max_sportsbook(self):
        return self._t1_max_sportsbook

    def _set_t1_max_sportsbook(self, t1_max_sportsbook: str):
        self._t1_max_sportsbook = t1_max_sportsbook

    # Team 2 getters/setters.
    def get_t2_name(self) -> str:
        return self._t2_name

    def get_t2_min(self) -> float:
        return self._t2_min

    def _set_t2_min(self, t2_min: float):
        self._t2_min = t2_min

    def get_t2_max(self) -> float:
        return self._t2_max

    def _set_t2_max(self, t2_max: float):
        self._t2_max = t2_max

    def get_t2_min_sportsbook(self):
        return self._t2_min_sportsbook

    def _set_t2_min_sportsbook(self, t2_min_sportsbook: str):
        self._t2_min_sportsbook = t2_min_sportsbook

    def get_t2_max_sportsbook(self):
        return self._t2_max_sportsbook

    def _set_t2_max_sportsbook(self, t2_max_sportsbook: str):
        self._t2_max_sportsbook = t2_max_sportsbook

    # Team 1 updates.
    def update_t1_min(self, t1_min: float, t1_min_sportsbook: str):
        self._set_t1_min(t1_min)
        self._set_t1_min_sportsbook(t1_min_sportsbook)

    def update_t1_max(self, t1_max: float, t1_max_sportsbook: str):
        self._set_t1_max(t1_max)
        self._set_t1_max_sportsbook(t1_max_sportsbook)

    # Team 2 updates.
    def update_t2_min(self, t2_min: float, t2_min_sportsbook: str):
        self._set_t2_min(t2_min)
        self._set_t2_min_sportsbook(t2_min_sportsbook)

    def update_t2_max(self, t2_max: float, t2_max_sportsbook: str):
        self._set_t2_max(t2_max)
        self._set_t2_max_sportsbook(t2_max_sportsbook)