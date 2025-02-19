import time
from testdriver import testdriver

def test_incolumitas():
    d = testdriver()
    d.get_page('https://bot.incolumitas.com/')
    time.sleep(300)

def test_sannysoft():
    d = testdriver()
    d.get_page('https://bot.sannysoft.com/')
    time.sleep(300)

# test_incolumitas()
test_sannysoft()