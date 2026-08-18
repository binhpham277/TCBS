# MAKE NEW ORDERS - BUYING / Building new positions
#=======================================================

import os
import pandas as pd
import json

# Authentication
#=======================================================
from tcbs import TCBSClient
import TCBS_ACC

from dotenv import load_dotenv
load_dotenv(r"D:/API/API_KEYS.env")
TCBS_API_KEY = os.getenv("TCBS_API_KEY")
client = TCBSClient(api_key=TCBS_API_KEY)

# Account Definition
#==================
accountMargin = TCBS_ACC.TCBS_ACC.Margin
accountNormal = TCBS_ACC.TCBS_ACC.Normal
#accountDerivative = TCBS_ACC.TCBS_ACC.Derivative
#Custody = TCBS_ACC.TCBS_ACC.Custody


#=====================================
# CONFIG
#====================================

# trading mode ===============
# mode = 1 		live trading
# mode = 0 		testing

trading_mode = 1


#=========================
# GET ASSETS REPORT - ASR
#=========================
assets = client.get_asset(account_no=accountMargin)
dfA = pd.DataFrame(assets)['stock']
assetsInfo = []
for symbol in dfA:
	assetsInfo.append({
		"symbol": symbol['symbol'],
		"availableTrading": symbol['availableTrading'],
		"currentPrice": symbol['currentPrice'],
		"costPrice": symbol['costPrice'],
		"quantity": symbol['totalQtty']
		})
resultsDfA = pd.DataFrame(assetsInfo)


#=========================
# Loading data before POST
#=========================

Sells = []
for row in resultsDfA.itertuples():
	Sells.append({
		"symbol": row[1],
		"Q": int(row[2]),
		"price": row[3],
		"OddLot": int(row[2])%100,
		"Q100": int(row[2]) - int(row[2])%100
		})
df_Sells = pd.DataFrame(Sells)
print(df_Sells)
print(len(df_Sells))

# GET ask pairs
markets = client.get_market_info(index=1)['data']	#HOSE
df_markets = pd.DataFrame(markets)
df_askPrices = pd.DataFrame(df_markets, columns = ['symbol','offerPrice01'])
#print(df_askPrices)

# combine 2 dataframes to get bid prices for new buys
if len(df_Sells) == 0:
	df_PostingSells = df_Sells
else:
	df_PostingSells = pd.merge(df_Sells, df_askPrices)
print(df_PostingSells)


#============================
# POST MNO - MAKE NEW ORDERS
#============================

def order_entry_buy(trading_mode, acount, symbol, sell_price, quantity):
	if trading_mode == 1:
		order = client.place_order(acount, symbol, 'NS', sell_price, quantity, 'LO')
	else:
		pass

for row in df_PostingSells.itertuples():

	symbol = row[1]
	sell_price = row[6]	# sell price - market
	price = row[3]		# price on the book
	Q100 = row[5]
	OddLOT = row[4]

	if Q100 > 0:
		
		confirmation = (f"placing sell for: {symbol}, at price: {sell_price/1000}, quantity: {Q100}\n")
		print(confirmation)

		#order = client.place_order(accountMargin, symbol, 'NS', sell_price, Q100, 'LO')
		order_entry_buy(trading_mode, accountMargin, symbol, sell_price, Q100)
	
	if OddLOT > 0:
		
		confirmation = (f"placing sell for: {symbol}, at price: {sell_price/1000}. quantity: {OddLOT}")
		print(confirmation)

		Oddlot10 = (OddLOT//10)*10
		leftOver = OddLOT - Oddlot10
		Oddlot5 = (leftOver//5)*5
		Oddlot1 = leftOver - Oddlot5
		print(f"{symbol}, Total oddlot: {OddLOT}, lot10: {Oddlot10} lot5: {Oddlot5}, lot1: {Oddlot1}\n")

		if Oddlot10 > 0:
			#order = client.place_order(accountMargin, symbol, 'NS', sell_price, Oddlot10, 'LO')
			order_entry_buy(trading_mode, accountMargin, symbol, sell_price, Oddlot10)
			
		if Oddlot5 > 0:
			#order = client.place_order(accountMargin, symbol, 'NS', sell_price, Oddlot5, 'LO')
			order_entry_buy(trading_mode, accountMargin, symbol, sell_price, Oddlot5)
			
		if Oddlot1 > 0:
			#order = client.place_order(accountMargin, symbol, 'NS', sell_price, Oddlot1, 'LO')
			order_entry_buy(trading_mode, accountMargin, symbol, sell_price, Oddlot1)
