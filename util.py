import numpy as np

promotion = 'undefined'

class american:
    def to_decimal(odds: str) -> float:
        n: int = int(odds[1:])
        prefix: str = odds[0]
        return (n + 100)/100 if prefix == '+' else (n + 100)/n

def compute_arb(t1_odds, t2_odds):
    return (1/t1_odds) + (1/t2_odds)

class random_normal:
    arr_len = 100

    short_interaction_times = np.random.normal(1.5, 0.25, arr_len)
    short_interaction_time_idx = 0

    long_interaction_times = np.random.normal(3.5, 0.40, arr_len)
    long_interaction_time_idx = 0

    def short_interaction_time() -> float:
        t = random_normal.short_interaction_times[random_normal.short_interaction_time_idx]
        random_normal.short_interaction_time_idx = (random_normal.short_interaction_time_idx + 1) % random_normal.arr_len
        return t

    def long_interaction_time() -> float:
        t = random_normal.long_interaction_times[random_normal.long_interaction_time_idx]
        random_normal.long_interaction_time_idx = (random_normal.long_interaction_time_idx + 1) % random_normal.arr_len
        return t

    def get(center, std):
        res = np.random.normal(center, std, 1)
        return res[0]