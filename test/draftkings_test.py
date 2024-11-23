from apis import draftkings

def test_stubbed_page():
    page = draftkings.get_page('football', 'nfl')
    assert page

test_stubbed_page()