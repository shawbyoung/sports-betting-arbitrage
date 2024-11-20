from src.sportsbook_apis.draftkings_api import draftkings_api

def test_stubbed_page():
    page = draftkings_api.get_page('football', 'nfl')
    assert page

test_stubbed_page()