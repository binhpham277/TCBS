# TCBS
Python scripts for traders using Techcom Securities (TCBS) API

MKI_SIG is a tool to generate sigma report from all equities market, using optimized 11 trading days period.
It also generates an expected win loss ratio based on number of trades from TCBS side.
Data is used from Vnstock.

Portfolio_Indexing:
Portfolio builder is another tool to quickly build a market cap weighted baskets.
Number of stocks can be defined at the top; any number is valid. Could be 50 or even 300.
You need to download a data excel file from TCBS (under filter) first and change the path so the engine can read it.
Each run is a new rebalancing of the account based on current market caps, account size and market prices.

In case of full liquidation, use MNO_FLATTEN to quickly send full sell orders to TCBS.
