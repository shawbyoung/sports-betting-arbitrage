import scipy.stats as stats
import time
import logger
import os
import fnmatch
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

promotion = None
profiles_dir = r"C:\Users\shawb\AppData\Local\Google\Chrome\User Data\\"
chromedriver_path = 'chromedriver/chromedriver.exe'
max_login_retries = 2

def find(pattern, path):
    matches = []
    # Use scandir for efficient directory listing
    with os.scandir(path) as entries:
        for entry in entries:
            # Compare the entry name against the pattern
            if fnmatch.fnmatch(entry.name, pattern):
                # Append the full path
                matches.append(entry.path)
    return matches

class american:
    def to_decimal(odds: str) -> float:
        n: int = int(odds[1:])
        prefix: str = odds[0]
        return (n + 100)/100 if prefix == '+' else (n + 100)/n

def compute_arb(t1_odds, t2_odds):
    return (1/t1_odds) + (1/t2_odds)

class simulate:
    _t_arr_len = 100

    _type_t_mu, _type_t_sig = 0.15, 0.05
    _type_t_l, _type_t_u = 0, 0.3
    _type_t = stats.truncnorm((_type_t_l - _type_t_mu) / _type_t_sig, (_type_t_u - _type_t_mu) / _type_t_sig, loc=_type_t_mu, scale=_type_t_sig).rvs(_t_arr_len)
    _type_t_idx = 0

    _short_t_mu, _short_t_sig = 1.5, 0.25
    _short_t_l, _short_t_u = 0.75, 2.25
    _short_t = stats.truncnorm((_short_t_l - _short_t_mu) / _short_t_sig, (_short_t_u - _short_t_mu) / _short_t_sig, loc=_short_t_mu, scale=_short_t_sig).rvs(_t_arr_len)
    _short_t_idx = 0

    _long_t_mu, _long_t_sig = 3.5, 0.5
    _long_t_l, long_t_u = 2.5, 5
    _long_t = stats.truncnorm((_long_t_l - _long_t_mu) / _long_t_sig, (long_t_u - _long_t_mu) / _long_t_sig, loc=_long_t_mu, scale=_long_t_sig).rvs(_t_arr_len)
    _long_t_idx = 0

    # TODO: explore conditional waits via selenium.
    def exact_wait(t):
        time.sleep(t)

    def click_short_wait(element):
        time.sleep(simulate.short_interaction_time())
        element.click()

    def click_long_wait(element):
        time.sleep(simulate.long_interaction_time())
        element.click()

    def short_wait():
        time.sleep(simulate.short_interaction_time())

    def long_wait():
        time.sleep(simulate.long_interaction_time())

    def wait_for_element(webdriver, wait_time, by, value):
        WebDriverWait(webdriver, wait_time).until(
			EC.presence_of_element_located((by, value))
		)
    def _type(input_element, text):
        for c in text:
            time.sleep(simulate.type_char_interaction_time())
            input_element.send_keys(c)

    def clear_and_type_in_field(input_element, text):
        if input_element.get_attribute("value") == text:
            return

        input_element.clear()
        simulate._type(input_element, text)

    def type_in_field(input_element, text) -> None:
        if input_element.get_attribute("value") == text:
            return

        simulate._type(input_element, text)

    def type_char_interaction_time() -> float:
        t = simulate._type_t[simulate._type_t_idx]
        simulate._type_t_idx = (simulate._type_t_idx + 1) % simulate._t_arr_len
        return t

    def short_interaction_time() -> float:
        t = simulate._short_t[simulate._short_t_idx]
        simulate._short_t_idx = (simulate._short_t_idx + 1) % simulate._t_arr_len
        return t

    def long_interaction_time() -> float:
        t = simulate._long_t[simulate._long_t_idx]
        simulate._long_t_idx = (simulate._long_t_idx + 1) % simulate._t_arr_len
        return t