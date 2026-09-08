# TCBS
Python scripts for traders using Techcom Securities (TCBS) API

Dependencies:
tcbs (https://pypi.org/project/tcbs/#description)
vnstock (https://github.com/vnstock-hq)


MKI_SIG (Market Index & Signal)
-------------------------------
MKI_SIG is a tool to generate sigma report from all equities market, using optimized 11 trading days period.
As I use VNIndex to calculate overall market volatility for some measures, this tool will download VNIndex data to an Excel file.
Sigmas are generated for the most recent 5 days per market for more thorough criteria, as some won't enter a new buy for 2 consecutive 2 sigmas event and some will.
eHD is short for expected Holding Days. In my recent trading practice, I normally hold eHDx2 as historically I tend to close trades prematuredly.
A hypothetic win-loss ratio (WLR) is also calculated based on the number of intraday trades from TCBS side.
Historical Daily price Data is provided using Vnstock API.

MPL (Market Price Levels)
-------------------------
This engine is designed to generate some key price levels based on observed clusters.
When there are no clear clusters, it will take the standard deviation of prices as a core consideration for calculation.
This engine calculates based on 100 days lookback, can be adjusted.
Currently MPL is designed for the long side, as Vietnamese Equities Market is not yet available for short selling, 
but it can be tweaked for the short side as well (list_up -> list_down).

Portfolio_Indexing
------------------
Portfolio_Indexing is builder for a market cap weighted basket. You own your index fund with read stocks.
Number of stocks can be defined at the very top; any number is valid. Could be 50 (for VN50) or even 186 for your own basket of 186 major stocks.
The engine needs an Excel data file (download from TCBS / Filter) to read and run.
Currently it is setup to build inside the normal account but can be changed to margin account easily.
Each run is a new rebalancing of the account based on current market caps, account size and market prices.
This tool is handy for traders who want a real equities basket, or who really do not like the idea of ETF or mutual fund indexing funds.
Technically, buying an ETF or an indexing fund is easier, but hey I like to see my stocks in the cash account as I have some unused money there.

MNO_FLATTEN (Full liquidation)
------------------------------
This will send a full batch of sell orders to TCBS.
Use this or Portfolio_Indexing before going on vacation is a smart choice.

MC Report
---------
MC Report is Monte-Carlo report which tests the edge of trading system.
This engine is simple and it takes basic inputs: probability for win/loss, and average win/loss

MPP (Making Push/Pull)
----------------------
This simple engine is designed to do one simple thing: move the price of existing orders to the closest bid/ask so the orders can be filled more quickly.
The engine will randomly check the cash account and margin account to see if there is any pending fill.
If the trading price is far from bid1/ask1 pair, it will change the price to bid1 for buy and ask1 for sell accordingly.
In my trading practice, this engine is scheduled to run every few minutes.


Disclaimer
----------
This library is personal written tools that author used in his trading process. It is not trading recommendation or investment advice.
This library is provided "as is" without warranty of any kind. Trading involves substantial risk of loss.
Always verify your code and test thoroughly before executing real trades.
The author is not responsible for any financial losses incurred through the use of this library.
