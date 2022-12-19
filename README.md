# arb3
Crypto Exchange Trading Platform written in Python and PostgreSQL
#MIT

Simple crypto trading application written in Python. I used a factory method pattern to abstract away the different exchange APIs, 
providing one API to call for every exchange. It should be simple to add additional exchanges. 

It's also simple to develop new trading strategies based on existing strategies provided. 

It uses PostgreSQL to log the trade information and strategy progress. 

It also supports SMS notification when a trade completes. 
