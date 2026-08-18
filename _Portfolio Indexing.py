# THIS ENGINE WILL BUILD AN INDEXING PORTFOLIO, MARKET CAP WEIGHTED
#==================================================================

from tcbs import TCBSClient
import TCBS_ACC

import pandas as pd
import os
import math
import time

from datetime import date
today = date.today()
print(f"Date: {today}")
filter_date = str(today)[5:7] + str(today)[-2:]+ str(today)[:4]

# EXCEL logs folder =============
# Change to where you want to save Excel logs
from pathlib import Path
EXCEL_OUTPUT_FOLDER = Path(r"D:/Dropbox/BXCapitals/TCBS_INDEXING/Excels")
EXCEL_OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

def save_excel(df, filename):
    filepath = EXCEL_OUTPUT_FOLDER / filename
    df.to_excel(filepath, index=False)
    print(f"Saved: {filepath}")


# AUTHENTICATION ==================
# LOAD your TCBS API key using dotenv file
from dotenv import load_dotenv
load_dotenv(r"D:/API/API_KEYS.env")
TCBS_API_KEY = os.getenv("TCBS_API_KEY")
client = TCBSClient(api_key=TCBS_API_KEY)

# ACCOUNT INFO ==========
# Indexing position on Regular account
accountNormal = TCBS_ACC.TCBS_ACC.Normal

# TRADING COST (CURRENT TCBS Scheme)
trading_cost = 0.03
tax = 0.1


# 0. MASTER CONFIG ===============================================================

# 1. Load new data
# 2. Update Account Value

# Load new data using Filter from TCBS (all market) to get market cap info
dataFileName = "BộLọc_Market All_" + filter_date
#print(dataFileName)
import shutil
source = rf"C:/Users/ACER/Downloads/{dataFileName}.xlsx"
destination = rf"D:/Dropbox/BXCapitals/TCBS_INDEXING/Market_Data_TCBS/{dataFileName}.xlsx"
shutil.copy(source, destination)
print("Data file copied successfully!")

dataPath = rf"D:/Dropbox/BXCapitals/TCBS_INDEXING/Market_Data_TCBS/{dataFileName}.xlsx"



# GET ASSET REPORT
asset = client.get_asset(accountNormal)['stock']
#print(asset)
pd_asset = pd.DataFrame(asset)
stock_value = (pd_asset['currentPrice'] * pd_asset['totalQtty']).sum()
print(pd_asset)
print(f"stocks value: {stock_value}")

cash = client.get_cash_investment(accountNormal)['data'][0]
cash_balance = cash.get('cashBalance')
#print(type(cash))
#print(len(cash))
#print(cash)
print(f"cash balance: {cash_balance}")

# Total Current Account Value 
TCAV = stock_value + cash_balance
print(f"total current account value: {TCAV}")


# TOTAL ACCOUNT VALUE (INCLUDING CASH-IN AND CURRENT EQUITIES)
# put zero to flatten the porfolio if needed
# unit: trieu dong
capital = TCAV/1000000
print(f"capital (in millions): {capital}")


#======================================
# Scope of constituents
basketScope = 100

# Buffer % for prices fluctuation during process of buying/selling
cash_buffer = 99

# Trading mode (1 = ok trading, 0 = testing)
trading_mode = 1


# I. BULIDING PENDING BUY SELL POSITIONS =========================================

AccountValue = capital * 1000000 * cash_buffer / 100

# MARKET CAPITALIZATION DATA =================================

data = pd.read_excel(dataPath, sheet_name = 'Filters')
data_filtered = pd.DataFrame(data, columns = ['Ticker','Exchange','Market Cap'])

data1 = []
for row in data_filtered.itertuples():
	data1.append({
		"symbol":row[1],
		"Exchange": row[2],
		"Market Cap": row[3]
		})

df_data1 = pd.DataFrame(data1)
save_excel(df_data1, f"{today}_1_0_Data_allmarket.xlsx")


condition2 = data_filtered['Market Cap'] > 0
data2 = data_filtered[condition2]

# threshold for the largest stocks based on market cap value
threshold = data2["Market Cap"].sort_values(ascending=False).iloc[basketScope]
#print(f"Threshold for market cap: {threshold}")

condition3 = data2['Market Cap'] > threshold
data3 = data2[condition3]
data3.reset_index(drop=True, inplace=True)
data3 = data3.rename(columns={"Ticker": "symbol"})

totalMarketCap = data3["Market Cap"].sum()
#print(f"Total Market Cap: {totalMarketCap} ty dong")

# threshold 100 ==============
# refference and study purpose
# ============================
threshold_100 = data2["Market Cap"].sort_values(ascending=False).iloc[100]
condition_100 = data2['Market Cap'] > threshold_100
data100 = data2[condition_100]
data100.reset_index(drop=True, inplace=True)
totalMarketCap100 = data100["Market Cap"].sum()

proportion100 = totalMarketCap100 / totalMarketCap * 100
print(f"top 100 stocks over the basket: {proportion100} %")


# add % allocation based on market cap
data_passThreshold = []
for row in data3.itertuples():
	data_passThreshold.append({
		"symbol":row[1],
		"Exchange": row[2],
		"Market Cap": row[3],
		"Allocation_PCT": row[3]/totalMarketCap,
		"Allocation_CASH": row[3]/totalMarketCap*AccountValue
		})

df_data_passThreshold = pd.DataFrame(data_passThreshold)
save_excel(df_data_passThreshold, f"{today}_1_1_Data_passThreshold.xlsx")


# MARKET TRADING DATA =========

market_HOSE = client.get_market_info(index=1)['data']
df_market_HOSE = pd.DataFrame(market_HOSE, columns = ['symbol','matchPrice','bidPrice01','offerPrice01','bidPrice02','offerPrice02','bidPrice03','offerPrice03','refPrice'])
#print(df_market_HOSE)

market_HNX = client.get_market_info(index=3)['data']
df_market_HNX = pd.DataFrame(market_HNX, columns = ['symbol','matchPrice','bidPrice01','offerPrice01','bidPrice02','offerPrice02','bidPrice03','offerPrice03','refPrice'])
#print(df_market_HNX)

market_UPCOM = client.get_market_info(index=5)['data']
df_market_UPCOM = pd.DataFrame(market_UPCOM, columns = ['symbol','matchPrice','bidPrice01','offerPrice01','bidPrice02','offerPrice02','bidPrice03','offerPrice03','refPrice'])
#print(df_market_UPCOM)

df_concat_1 = pd.concat([df_market_HOSE, df_market_HNX], ignore_index=True)
df_concat_2 = pd.concat([df_concat_1, df_market_UPCOM], ignore_index=True)

df_market = df_concat_2
df_market.reset_index(drop=True, inplace=True)
save_excel(df_market, f"{today}_1_2_Market_all_tradingData.xlsx")

# MERGING =============

df_MarketInfo = pd.merge(df_data_passThreshold, df_market)
save_excel(df_MarketInfo, f"{today}_1_3_Target_Porfolio.xlsx")

marketOutlook = []
for row in df_MarketInfo.itertuples():
	marketOutlook.append({
		"symbol": row[1],
		"Exchange": row[2],
		"Market Cap": row[3],
		"Percentage": row[4],
		"Cash Allocation": row[5],
		"Target Shares": row[5]/row[13], #(using ref Price to calculate)
		"matchPrice": row[6],
		"bidPrice01": row[7],
		"offerPrice01": row[8],
		"bidPrice02": row[9],
		"offerPrice02": row[10],
		"bidPrice03": row[11],
		"offerPrice03": row[12],
		"refPrice": row[13]
		})

df_marketOutlook = pd.DataFrame(marketOutlook)
df_marketOutlook["Target Shares"] = df_marketOutlook["Target Shares"].fillna(0).astype(int)
save_excel(df_marketOutlook, f"{today}_1_4_Target_Porfolio_with_Target_Shares.xlsx")


# ACOUNT STATUS ============================================

# Assets Available For Trading
assets = client.get_asset(account_no=accountNormal)
df_Assets = pd.DataFrame(assets)['stock']

assetsReadyToTrade = []	#list
for symbol in df_Assets:
	if symbol['availableTrading'] > 0:
		assetsReadyToTrade.append({
			"symbol": symbol['symbol'],
			"availTrading": symbol['availableTrading'],
			"currentPrice": symbol['currentPrice']/1000,
			"quantityBook": symbol['totalQtty'],
			})
	else:
		assetsReadyToTrade.append({
			"symbol": symbol['symbol'],
			"availTrading": symbol['availableTrading'],
			"currentPrice": symbol['currentPrice']/1000,
			"quantityBook": symbol['totalQtty'],
			})

df_ARTT = pd.DataFrame(assetsReadyToTrade)
save_excel(df_ARTT, f"{today}_1_5_ARTT.xlsx")

# add Prices and Exchange to ASSET BOOKS
df_AssetsBook1 = df_ARTT.merge(df_data1, on="symbol", how="left")
df_AssetsBook2 = df_AssetsBook1.merge(df_market, on="symbol", how="left")

df_AssetsBook = df_AssetsBook2
save_excel(df_AssetsBook, f"{today}_1_6_AssetsBook.xlsx")


# TRACKER =============================================

df_Tracker_currentStatus = (
    pd.concat([df_marketOutlook, df_AssetsBook])
      .groupby("symbol", as_index=False)
      .first()
)

# fill in 0 numerical value for empty cell
df_Tracker_currentStatus["quantityBook"] = df_Tracker_currentStatus["quantityBook"].fillna(0).astype(int)
df_Tracker_currentStatus["Target Shares"] = df_Tracker_currentStatus["Target Shares"].fillna(0).astype(int)

save_excel(df_Tracker_currentStatus, f"{today}_1_7_Tracker_currentStatus.xlsx")


Tracker_sharesDifferences = []
for row in df_Tracker_currentStatus.itertuples():
	Tracker_sharesDifferences.append({
		"symbol": row[1],
		"Exchange": row[2],
		"Market Cap": row[3],
		"Allocation PCT": row[4],
		"Allocation CASH": row[5],
		"Target Shares": row[6],
		"Current Shares": row[17],
		"Shares Difference": row[6]-row[17],
		"bid1": row[8],
		"ask1": row[9],
		"bid2": row[10],
		"ask2": row[11],
		"bid3": row[12],
		"ask3": row[13],
		"ref Price": row[14]
		})

df_Tracker_sharesDifferences = pd.DataFrame(Tracker_sharesDifferences)
save_excel(df_Tracker_sharesDifferences, f"{today}_1_8_Tracker_sharesDifferences.xlsx")


# TRADING TRIGGER =======

# add Trigger Value to indicate buy/sell (1,-1)
import numpy as np
df_Tracker_sharesDifferences["Trigger"] = np.sign(df_Tracker_sharesDifferences["Shares Difference"]).astype(int)



# II. ORDER ENTRY ===========================================================

# PREPARE PENDING ORDERS ==========

df_Tracker_sharesDifferences['buy'] = np.where(df_Tracker_sharesDifferences['Shares Difference'] > 0, df_Tracker_sharesDifferences['Shares Difference'], 0)
df_Tracker_sharesDifferences['sell'] = np.where(df_Tracker_sharesDifferences['Shares Difference'] < 0, df_Tracker_sharesDifferences['Shares Difference']*-1, 0)

save_excel(df_Tracker_sharesDifferences, f"{today}_1_9_Tracker_sharesDifferences_Trigger.xlsx")

#fill in numerical value for bid/ask pairs
df_Tracker_sharesDifferences["bid1"] = df_Tracker_sharesDifferences["bid1"].fillna(0).astype(int)
df_Tracker_sharesDifferences["bid2"] = df_Tracker_sharesDifferences["bid2"].fillna(0).astype(int)
df_Tracker_sharesDifferences["bid3"] = df_Tracker_sharesDifferences["bid3"].fillna(0).astype(int)
df_Tracker_sharesDifferences["ask1"] = df_Tracker_sharesDifferences["ask1"].fillna(0).astype(int)
df_Tracker_sharesDifferences["ask2"] = df_Tracker_sharesDifferences["ask2"].fillna(0).astype(int)
df_Tracker_sharesDifferences["ask3"] = df_Tracker_sharesDifferences["ask3"].fillna(0).astype(int)
df_Tracker_sharesDifferences["ref Price"] = df_Tracker_sharesDifferences["ref Price"].fillna(0).astype(int)


pendingPosition = []

for row in df_Tracker_sharesDifferences.itertuples():

	#closest bid/ask of 2 pairs
	best_bid = max(row[9], row[11], row[13])
	best_ask = min(row[10], row[12], row[14])

	# including ref price in case there's no current bid/asl
	bid_prices = [best_bid, row[15]]
	ask_prices = [best_ask, row[15]]

	trading_prices = [best_bid,best_ask, row[15]]

	bid_non_zero = [x for x in trading_prices if x not in (0, None)]
	ask_non_zero = [x for x in trading_prices if x not in (0, None)]

	pendingPosition.append({
		"symbol": row[1],
		"quantity_buy": row[17],
		"Q_B_100": int(row[17]) - int(row[17])%100,
		"Q_B_Oddlot": int(row[17])%100,
		"quantity_sell": row[18],
		"Q_S_100": int(row[18]) - int(row[18])%100,
		"Q_S_Oddlot": int(row[18])%100,
		"bid price": best_bid/1000,
		"ask price": best_ask/1000,
		"refPrice": row[15]/1000,
		"buy price": min(bid_non_zero),
		"sell price": max(ask_non_zero),
		"buy_value": row[17] * min(bid_non_zero),
		"sell_value": row[18] * max(ask_non_zero)
		})

df_pendingPosion = pd.DataFrame(pendingPosition)



#drop row where both buy & sell is zero
df_pendingPosion = df_pendingPosion[~((df_pendingPosion["quantity_buy"] == 0) & (df_pendingPosion["quantity_sell"] == 0))]
save_excel(df_pendingPosion, f"{today}_2_0_PendingPosion.xlsx")

df_pendingPosion.reset_index(drop=True, inplace=True)
print(df_pendingPosion)


# COST ESTIMATION
# =====================================

total_buy_value = df_pendingPosion['buy_value'].sum()
total_sell_value = df_pendingPosion['sell_value'].sum()

cost_buy = total_buy_value * trading_cost / 100
cost_sell = total_sell_value * (trading_cost + tax) / 100
total_cost = cost_buy + cost_sell
total_cost_pct = total_cost/TCAV*100

print(f"trading cost in $: {f'{total_cost:.2f}'} VND")
print(f"trading cost in %: {total_cost_pct} %")


from openpyxl import load_workbook
FILE = "_log_trading_cost.xlsx"
# Open existing workbook
wb = load_workbook(FILE)
# Select worksheet
ws = wb["Sheet1"]
# New row
new_row = [today, total_cost, total_cost_pct]
# Append the row
ws.append(new_row)
# Save
wb.save(FILE)
print("logged trading cost to Excel!")


# ORDER ENTRY ===========================================

for row in df_pendingPosion.itertuples():

	tradeNo = row[0]

	symbol = row[1]

	total_buy = row[2]
	total_sell = row[5]

	Q_B_100 = row[3]
	Q_B_Oddlot = row[4]
	buy_price = row[11]

	Q_S_100 = row[6]
	Q_S_Oddlot = row[7]
	sell_price = row[12]

	def order_entry_buy(trading_mode, account, symbol, buy_price, quantity):
		if trading_mode == 1:
			order = client.place_order(account, symbol, 'NB', buy_price, quantity, 'LO')
		else:
			pass

	def order_entry_sell(trading_mode, account, symbol, sell_price, quantity):
		if trading_mode == 1:
			order = client.place_order(account, symbol, 'NS', sell_price, quantity, 'LO')
		else:
			pass

	# BUY ===============================================
	print(f"PLACING BUY {total_buy} SHARES for {symbol}")
	if Q_B_100 > 0:

		confirmation = (f"Trade no.{tradeNo}: placing buy for: {symbol}, at price: {buy_price/1000}, quantity: {Q_B_100}")
		print(confirmation)

		print(f"order = client.place_order(accountNormal, {symbol}, 'NB', {buy_price}, {Q_B_100}, 'LO')")
		order_entry_buy(trading_mode, accountNormal, symbol, buy_price, Q_B_100)

	if Q_B_Oddlot > 0:

		confirmation = (f"Trade no.{tradeNo}: placing buy for: {symbol}, at price: {buy_price/1000}, quantity: {Q_B_Oddlot}")
		print(confirmation)

		Oddlot10 = (Q_B_Oddlot//10)*10
		leftOver = Q_B_Oddlot - Oddlot10
		Oddlot5 = (leftOver//5)*5
		Oddlot1 = leftOver - Oddlot5
		print(f"{symbol}, Total oddlot: {Q_B_Oddlot}. lot10: {Oddlot10} lot5: {Oddlot5}, lot1: {Oddlot1}")

		if Oddlot10 > 0:
			print(f"order = client.place_order(accountNormal, {symbol}, 'NB', {buy_price}, {Oddlot10}, 'LO')")
			order_entry_buy(trading_mode, accountNormal, symbol, buy_price, Oddlot10)
			
		if Oddlot5 > 0:
			print(f"order = client.place_order(accountNormal, {symbol}, 'NB', {buy_price}, {Oddlot5}, 'LO')")
			order_entry_buy(trading_mode, accountNormal, symbol, buy_price, Oddlot5)
			
		if Oddlot1 > 0:
			print(f"order = client.place_order(accountNormal, {symbol}, 'NB', {buy_price}, {Oddlot1}, 'LO')")
			order_entry_buy(trading_mode, accountNormal, symbol, buy_price, Oddlot1)

	print("\n")

	# SELL =================================================
	print(f"PLACING SELL {total_sell} SHARES for {symbol}")
	if Q_S_100 > 0:

		confirmation = (f"Trade no.{tradeNo}: placing sell for: {symbol}, at price: {sell_price/1000}, quantity: {Q_S_100}")
		print(confirmation)

		print(f"order = client.place_order(accountNormal, {symbol}, 'NS', {sell_price}, {Q_S_100}, 'LO')")
		order_entry_sell(trading_mode, accountNormal, symbol, sell_price, Q_S_100)

	if Q_S_Oddlot > 0:

		confirmation = (f"Trade no.{tradeNo}: placing sell for: {symbol}, at price: {sell_price/1000}, quantity: {Q_S_Oddlot}")
		print(confirmation)

		Oddlot10 = (Q_S_Oddlot//10)*10
		leftOver = Q_S_Oddlot - Oddlot10
		Oddlot5 = (leftOver//5)*5
		Oddlot1 = leftOver - Oddlot5
		print(f"{symbol}, Total oddlot: {Q_S_Oddlot}. lot10: {Oddlot10} lot5: {Oddlot5}, lot1: {Oddlot1}")

		if Oddlot10 > 0:
			print(f"order = client.place_order(accountNormal, {symbol}, 'NS', {sell_price}, {Oddlot10}, 'LO')")
			order_entry_sell(trading_mode, accountNormal, symbol, sell_price, Oddlot10)
			
		if Oddlot5 > 0:
			print(f"order = client.place_order(accountNormal, {symbol}, 'NS', {sell_price}, {Oddlot5}, 'LO')")
			order_entry_sell(trading_mode, accountNormal, symbol, sell_price, Oddlot5)
			
		if Oddlot1 > 0:
			print(f"order = client.place_order(accountNormal, {symbol}, 'NS', {sell_price}, {Oddlot1}, 'LO')")
			order_entry_sell(trading_mode, accountNormal, symbol, sell_price, Oddlot1)

	print("\n")


# FINISH
# ======================================

print("Successful!")
print("See you next week!")

#import yfinance as yf
#ticker = yf.Ticker("VND=X")
#USDrate = ticker.history(period="1d")["Close"].iloc[-1]
#print(f"USD/VND = {USDrate:.2f}")
#portfolio_value_in_dollar = round((captital / USDrate), 3)
#print(f"built a portfolio of {portfolio_value_in_dollar} millions dollar")

