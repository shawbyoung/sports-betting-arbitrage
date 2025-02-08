import numpy as np
import time

promotion = 'undefined'

class american:
    def to_decimal(odds: str) -> float:
        n: int = int(odds[1:])
        prefix: str = odds[0]
        return (n + 100)/100 if prefix == '+' else (n + 100)/n

def compute_arb(t1_odds, t2_odds):
    return (1/t1_odds) + (1/t2_odds)

class simulate:
    time_arr_len = 100

    type_char_interaction_times = np.random.normal(0.150, 0.25, time_arr_len)
    type_char_interaction_time_idx = 0

    short_interaction_times = np.random.normal(1.5, 0.25, time_arr_len)
    short_interaction_time_idx = 0

    long_interaction_times = np.random.normal(3.5, 0.40, time_arr_len)
    long_interaction_time_idx = 0

    def type_in_field(input_element, text) -> float:
        input_element.clear()
        for c in text:
            time.sleep(simulate.type_char_interaction_time())
            input_element.send_keys(c)

    def type_char_interaction_time() -> float:
        t = simulate.type_char_interaction_times[simulate.type_char_interaction_time_idx]
        simulate.type_char_interaction_time_idx = (simulate.type_char_interaction_time_idx + 1) % simulate.time_arr_len
        return t

    def short_interaction_time() -> float:
        t = simulate.short_interaction_times[simulate.short_interaction_time_idx]
        simulate.short_interaction_time_idx = (simulate.short_interaction_time_idx + 1) % simulate.time_arr_len
        return t

    def long_interaction_time() -> float:
        t = simulate.long_interaction_times[simulate.long_interaction_time_idx]
        simulate.long_interaction_time_idx = (simulate.long_interaction_time_idx + 1) % simulate.time_arr_len
        return t

    def get(center, std):
        res = np.random.normal(center, std, 1)
        return res[0]