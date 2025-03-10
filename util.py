import scipy.stats as stats
import time
from logger import logger
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

# TODO: implement state here, in config, and in individual drivers, eventually.
promotion = None

# Constants.

def chromedriver_path():
    return 'chromedriver/chromedriver.exe'

def max_login_retries():
    return 2

def post_login_timeout():
    return 30

class american:
    # TODO: implement a function called "is_plus" that returns if the prefix
    # is in the set of characters that are pluses and the complement for minuses.
    def to_decimal(odds: str) -> float:
        n: float = float(odds[1:])
        prefix: str = odds[0]
        return (n + 100.0)/100.0 if prefix == '+' else (n + 100.0)/n

def compute_profit(t1_odds: float, t2_odds: float) -> float:
    return (1.0/((1.0/t1_odds) + (1.0/t2_odds))) - 1

def compute_favorite_wager(bet_amt: float, favorite_odds: float, underdog_odds: float) -> float:
    return bet_amt / ((favorite_odds/underdog_odds) + 1.0)

def compute_underdog_wager(bet_amt: float, favorite_odds: float, underdog_odds: float) -> float:
    return (bet_amt * favorite_odds) / (favorite_odds + underdog_odds)

def round_wager(wager: float) -> int:
    return int(wager)

def compute_winnings(t1_wager: int, t1_odds: float, t2_wager: int, t2_odds: float) -> float:
    return (t1_wager * t1_odds) + (t2_wager * t2_odds) - t1_wager - t2_wager

class simulate:
    _t_arr_len = 100

    _type_t_mu, _type_t_sig = 0.15, 0.05
    _type_t_l, _type_t_u = 0, 0.3
    _type_t = stats.truncnorm(
        (_type_t_l - _type_t_mu) / _type_t_sig,
        (_type_t_u - _type_t_mu) / _type_t_sig,
        loc=_type_t_mu, scale=_type_t_sig).rvs(_t_arr_len)
    _type_t_idx = 0

    _short_t_mu, _short_t_sig = 1.5, 0.25
    _short_t_l, _short_t_u = 0.75, 2.25
    _short_t = stats.truncnorm(
        (_short_t_l - _short_t_mu) / _short_t_sig,
        (_short_t_u - _short_t_mu) / _short_t_sig,
        loc=_short_t_mu, scale=_short_t_sig).rvs(_t_arr_len)
    _short_t_idx = 0

    _long_t_mu, _long_t_sig = 3.5, 0.5
    _long_t_l, long_t_u = 2.5, 5
    _long_t = stats.truncnorm(
        (_long_t_l - _long_t_mu) / _long_t_sig,
        (long_t_u - _long_t_mu) / _long_t_sig,
        loc=_long_t_mu, scale=_long_t_sig).rvs(_t_arr_len)
    _long_t_idx = 0

    def exact_wait(t):
        time.sleep(t)

    # TODO: [safety] move impl to driver for no circular dependency when we to statically type this?
    # TODO: for failures at the driver/element level, we should we quit the webdriver and reinitialize it.
    def safe_click(driver, element: WebElement) -> bool:
        try:
            driver.execute_script("arguments[0].scrollIntoView()", element)
            element.click()
            return True
        except Exception as e:
            logger.log_error(f'Could not click element. Exception: {e}')
            return False

    def force_click(driver, element):
        driver.execute_script("arguments[0].click();", element)

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

    # TODO: [safety] move impl to driver for no circular dependency when we to statically type this?
    def wait_for_element(webdriver, wait_time, by, value):
        WebDriverWait(webdriver, wait_time).until(
			EC.presence_of_element_located((by, value))
		)

    def _type(input_element, text) -> bool:
        try:
            for c in text:
                time.sleep(simulate.type_char_interaction_time())
                input_element.send_keys(c)
            return True
        except Exception as e:
            return False

    def clear_and_type_in_field(input_element, text) -> bool:
        try:
            if input_element.get_attribute("value") == text:
                return True
            input_element.clear()
            return simulate._type(input_element, text)
        except Exception as e:
            return False

    def type_in_field(input_element, text) -> bool:
        try:
            if input_element.get_attribute("value") == text:
                return
            return simulate._type(input_element, text)
        except Exception as e:
            return False

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