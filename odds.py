import util
from logger import logger
from typing import Callable

def odds(
    sportsbook: str, promotion: str, participants: list[str], spread: list[str], 
    total: list[str], moneyline: list[str]
):
    total_idx = 1

    if participants[0] < participants[1]:
        t1_participants_idx = 0
        t2_participants_idx = 1
        t1_spread_idx = 1
        t2_spread_idx = 3
        t1_total_idx = 2
        t2_total_idx = 5
        t1_moneyline_idx = 0
        t2_moneyline_idx = 1
    else:
        t1_participants_idx = 1
        t2_participants_idx = 0
        t1_spread_idx = 3
        t2_spread_idx = 1
        t1_total_idx = 5
        t2_total_idx = 2
        t1_moneyline_idx = 1
        t2_moneyline_idx = 0

    t1_name = participants[t1_participants_idx]
    t2_name = participants[t2_participants_idx]

    event_odds = {
        'promotion' : promotion,
        'sportsbook' : sportsbook,
        't1_name' : t1_name,
        't2_name' : t2_name
    }

    print(sportsbook, spread)
    print(sportsbook, total)
    print(sportsbook, moneyline)

    if len(spread) == 4 & spread[t1_spread_idx][1:].isnumeric() & spread[t2_spread_idx][1:].isnumeric():		
        event_odds['t1_spread_odds'] = util.american.to_decimal(spread[t1_spread_idx])
        event_odds['t2_spread_odds'] = util.american.to_decimal(spread[t2_spread_idx])
    else:
        logger.log_warning(f'[{sportsbook}] {t1_name}, {t2_name} event has no valid spread info.')

    # consider dropping unnecessary information.
    # add some form of checking for odds format.
    if len(total) == 6:
        event_odds['total_score'] = total[total_idx]
        event_odds['t1_total_odds'] = util.american.to_decimal(total[t1_total_idx])
        event_odds['t2_total_odds'] = util.american.to_decimal(total[t2_total_idx])
    else:
        logger.log_warning(f'[{sportsbook}] {t1_name}, {t2_name} event has no total info.')

    # if len(moneyline) == 2 & moneyline[t1_moneyline_idx][1:].isnumeric() & moneyline[t1_moneyline_idx][1:].isnumeric():
    if len(moneyline) == 2:
        event_odds['t1_moneyline_odds'] = util.american.to_decimal(moneyline[t1_moneyline_idx])
        event_odds['t2_moneyline_odds'] = util.american.to_decimal(moneyline[t2_moneyline_idx])
    else:
        logger.log_warning(f'[{sportsbook}] {t1_name}, {t2_name} event has no moneyline info, dropping.')
        return None

    return event_odds