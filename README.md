1. Data retrieval
2. Bet finding
3. Bet execution 

1. I think we'll want to write our own APIs for different sports. 
Let's keep our scope small and stick to 2-3 sportsbooks to begin with.
We can do this with the request library. We can consider using JS for 
latency. Unlikely for that to be super useful though.
We can asynchronously call the api for each book to improve latency.

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


