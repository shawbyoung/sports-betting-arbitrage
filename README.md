1. Data retrieval
2. Bet finding
3. Bet execution 

1. I think we'll want to write our own APIs for different sports. 
Let's keep our scope small and stick to 2-3 sportsbooks to begin with.
We can do this with the request library. Consider using JS for 
latency? actually have no clue about that shit. i mean we could always do c++ 
but that seems lowkey ridiculous. our bottleneck isn't api anyways.

We should asynchronously call the api for each book to improve latency.

TODO: 
 - buildout api for draftkings
 - decide on internal representation for betting categories, e.g. 'nfl', 'green bay packers'
 - we should fail if it's not 1:1. we risk too much otherwise

2. Bet finding should follow what did historically in the last iteration of this.
We can considering writing C python library to improve latency here if that's a problem.
We should look into different benchmarking python libraries. 

3. For bet execution we can probably use something like selenium. We'll have to 
store account information carefully, gitignore type shit. Execution will likely be a bottleneck.
We can look into ways to improve latency later.

'''
This engine supports the following sportsbooks:
	- draftkings
The following betting sports/betting categories:  
	- NFL
The following kinds of bets:
	- head to head
And seeks to bet on purely pure arbitrage.
'''

Sports book selection
 - draftkings 
	- has been unfussy about requests and response is consistent w what you
 	  see in browser
 - betus 
	- browser shows no odds?
 - fanduel
	- i rec
 - bet365 
	- requests seem to fail
 - caesars 
	- does not have desktop website... lame
	- we could maybe find endpoints w android emulator or smth?
	- but is it worth the trouble? def not for early game
 - betriver
	- response seems to differ from what i see on browser. not sportsbook info,
	  seems to force authentification. which is fine tbh, with selenium. just 
	  changes design a tad that can be dealt w 
 - betmgm
	- i vaguely remember requests failing (?) verify
 - hardrock
	- desktop link hard to find tf

- checkout overtime markets, cloudbet, sportsbet.io 
 - crypto sportsbooks


Traceback (most recent call last):
  File "/home/shawy/sports-betting-arbitrage/main.py", line 7, in <module>
    main()
  File "/home/shawy/sports-betting-arbitrage/main.py", line 4, in main
    engine()
  File "/home/shawy/sports-betting-arbitrage/engine.py", line 13, in __init__
    asyncio.run(engine.bet(sportsbooks, promotions))
  File "/usr/lib/python3.10/asyncio/runners.py", line 44, in run
    return loop.run_until_complete(main)
  File "/usr/lib/python3.10/asyncio/base_events.py", line 649, in run_until_complete
    return future.result()
  File "/home/shawy/sports-betting-arbitrage/engine.py", line 93, in bet
    engine._find_arbitrage(list(chain.from_iterable(odds_nested)))
  File "/home/shawy/sports-betting-arbitrage/engine.py", line 26, in _find_arbitrage
    t1_moneyline_odds, t2_moneyline_odds = odds['t1_moneyline_odds'], odds['t2_moneyline_odds']
KeyError: 't1_moneyline_odds'


Traceback (most recent call last):
  File "/home/shawy/sports-betting-arbitrage/main.py", line 7, in <module>
    main()
  File "/home/shawy/sports-betting-arbitrage/main.py", line 4, in main
    engine()
  File "/home/shawy/sports-betting-arbitrage/engine.py", line 13, in __init__
    asyncio.run(engine.bet(sportsbooks, promotions))
  File "/usr/lib/python3.10/asyncio/runners.py", line 44, in run
    return loop.run_until_complete(main)
  File "/usr/lib/python3.10/asyncio/base_events.py", line 649, in run_until_complete
    return future.result()
  File "/home/shawy/sports-betting-arbitrage/engine.py", line 113, in bet
    odds_nested = await asyncio.gather(*coros)
  File "/home/shawy/sports-betting-arbitrage/driver.py", line 34, in collect_odds
    odds = await asyncio.gather(*coros)
  File "/home/shawy/sports-betting-arbitrage/betmgm.py", line 14, in _collect_nba_odds
    self.driver.get('https://sports.va.betmgm.com/en/sports/basketball-7/betting/usa-9/nba-6004')
  File "/home/shawy/.local/lib/python3.10/site-packages/selenium/webdriver/remote/webdriver.py", line 356, in get
    self.execute(Command.GET, {"url": url})
  File "/home/shawy/.local/lib/python3.10/site-packages/selenium/webdriver/remote/webdriver.py", line 347, in execute
    self.error_handler.check_response(response)
  File "/home/shawy/.local/lib/python3.10/site-packages/selenium/webdriver/remote/errorhandler.py", line 229, in check_response
    raise exception_class(message, screen, stacktrace)
selenium.common.exceptions.WebDriverException: Message: Failed to decode response from marionette