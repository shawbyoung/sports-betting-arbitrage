class american:
    def to_decimal(odds: str) -> float:
        n: int = int(odds[1:])
        prefix: str = odds[0]
        return (n + 100)/100 if prefix == '+' else (n + 100)/n

def compute_arb(t1_odds, t2_odds):
    return (1/t1_odds) + (1/t2_odds)

# def convert_odds_to_decimal(american_odds: int) -> float:
#     return (american_odds / 100) + 1