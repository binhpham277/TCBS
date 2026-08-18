# MARKET INDEX & SIGNALS
#=======================================================

import pandas as pd
import os
import math
import time


from tcbs import TCBSClient
import TCBS_ACC

from dotenv import load_dotenv
load_dotenv(r"D:/API/API_KEYS.env")
TCBS_API_KEY = os.getenv("TCBS_API_KEY")
client = TCBSClient(api_key=TCBS_API_KEY)

from vnstock import register_user
load_dotenv(r"D:/API/API_KEYS.env")
VNSTOCK_API_KEY = os.getenv("VNSTOCK_API_KEY")
register_user(VNSTOCK_API_KEY)

from tvDatafeed import TvDatafeed, Interval

#==========================================================================
#VNALLSHARE INDEX 500 trading days data
#======================================
tv = TvDatafeed(
    username=None,   # put username here if you have one
    password=None    # put password here if you have one
)
df = None
for attempt in range(3):
    try:
        df = tv.get_hist(
            symbol="VNALLSHARE",
            exchange="INDEX",
            interval=Interval.in_daily,
            n_bars=600
        )
        if df is not None and not df.empty:
            break
    except Exception:
        time.sleep(2)
if df is None or df.empty:
    raise RuntimeError("Try again later or login.")
df = df.tail(500)
df = df.reset_index()
df["datetime"] = df["datetime"].dt.tz_localize(None)
df.rename(columns={
    "datetime": "Date",
    "open": "Open",
    "high": "High",
    "low": "Low",
    "close": "Close",
    "volume": "Volume"
}, inplace=True)
df["Date"] = df["Date"].dt.strftime("%m/%d/%Y")
df.to_excel("Excel_MKI.xlsx", index=False)
print("\nMARKET INDEX updated\n")


#===========================================================================================
# TCBS List (HOSE)
marketList = client.get_market_info(index=1)['data']
allMarketList = pd.DataFrame(marketList, columns = ['symbol','totalVal'])
symbolsList = []
for row in allMarketList.itertuples():
	if row[2] > 0:
		symbolsList.append(row[1])
symbolListSet = list(set(symbolsList))
print(str(len(symbolListSet)) + " tickers for tcbs list\n")

# VNstock List
from vnstock import Listing
listing = Listing()
a = listing.symbols_by_group('VN100')
b = listing.symbols_by_group('VNMidCap')
c = listing.symbols_by_group('VNSmallCap')
marketList = list(a) + list(b) + list(c)
marketListSet = list(set(marketList))
print(str(len(marketListSet)) + " tickers for vnstock list\n")


#============================================================================================
#Look up  trading data and calculate sigma
#=========================================


def getData(symbol, period):
	from datetime import date, timedelta
        
	endDate = date.today()
	startDate = endDate - timedelta(days=int(period))
	endDate_str = str(endDate)
	startDate_str = str(startDate)

	sym = str(symbol)

	days = period
	lengthQ =f"{days}D"

	#from vnstock import Vnstock
	#stock = Vnstock().stock(symbol=sym, source='KBS')
	#quote = stock.quote.history(start=startDate_str, end=endDate_str)
        
	#from vnstock.ui import Market
	#mkt = Market()
	#quote = mkt.equity(sym).ohlcv(start=startDate_str, end=endDate_str, count=period)
    
	from vnstock import Quote
	quote = Quote(symbol=sym)
	df_quote = quote.history(end=endDate_str, length=lengthQ, interval="1D")

	return(df_quote)   #return a DataFrame

def Sigma(symbol, period):
	#Define lookup period = 400days, as we also calculate expected holding days
	#==========================================================================
	
	quoteData = getData(symbol, 400)
	print(f"getting data for: {symbol}")

	#indexing data for later calculation
	quoteDataIndexed = []
	for row in quoteData.itertuples():
		from datetime import date
		quoteDataIndexed.append({
			"index": row[0],
			"dateTime": row[1],
			"O": row[2],
			"H": row[3],
			"L": row[4],
			"C": row[5],
			"Volume": row[6]
			})
	df_quoteDataIndexed = pd.DataFrame(quoteDataIndexed)

	# Get %Changes from new OHLC to a new table
	quoteDataIndexed_withOHLC_percentageChange = []
	for row in df_quoteDataIndexed.itertuples():
		#first row will have no data as the previous day is null
		if row.index == 0:
			continue
		#Get C1234 into new table
		previousDay_O = df_quoteDataIndexed.loc[row.index - 1, "O"]
		previousDay_H = df_quoteDataIndexed.loc[row.index - 1, "H"]
		previousDay_L = df_quoteDataIndexed.loc[row.index - 1, "L"]
		previousDay_C = df_quoteDataIndexed.loc[row.index - 1, "C"]
		#print(row[2]) #timestamp
		#print(previousDay_O)
		#print(previousDay_H)
		#print(previousDay_L)
		#print(previousDay_C)
		# as %changes are used to calculate stdDev, we will list all possible OHLC
		O1 = row[3]/previousDay_O - 1
		O2 = row[3]/previousDay_H - 1
		O3 = row[3]/previousDay_L - 1
		O4 = row[3]/previousDay_C - 1
		H1 = row[4]/previousDay_O - 1
		H2 = row[4]/previousDay_H - 1
		H3 = row[4]/previousDay_L - 1
		H4 = row[4]/previousDay_C - 1
		L1 = row[5]/previousDay_O - 1
		L2 = row[5]/previousDay_H - 1
		L3 = row[5]/previousDay_L - 1
		L4 = row[5]/previousDay_C - 1
		#C1234 is %change of C to previous OHLC
		C1 = row[6]/previousDay_O - 1
		C2 = row[6]/previousDay_H - 1
		C3 = row[6]/previousDay_L - 1
		C4 = row[6]/previousDay_C - 1
		# %change of C to the same day trading session
		CL = row[6]/row[5] - 1
		CH = row[6]/row[4] - 1
		CO = row[6]/row[3] - 1
		quoteDataIndexed_withOHLC_percentageChange.append({
			"index": row[1],
			"dateTime": row[2],
			"O": row[3],
			"H": row[4],
			"L": row[5],
			"C": row[6],
			"Volume": row[7],
			"O1": O1,
			"O2": O2,
			"O3": O3,
			"O4": O4,
			"H1": H1,
			"H2": H2,
			"H3": H3,
			"H4": H4,
			"L1": L1,
			"L2": L2,
			"L3": L3,
			"L4": L4,
			"C1": C1,
			"C2": C2,
			"C3": C3,
			"C4": C4,
			"min": min(C1,C2,C3,C4,CL,CH,CO),
			"max": max(C1,C2,C3,C4,CL,CH,CO)
			})
	df_quoteDataIndexed_withOHLC_percentageChange = pd.DataFrame(quoteDataIndexed_withOHLC_percentageChange)
	#print(df_quoteDataIndexed_withOHLC_percentageChange)
	#df_quoteDataIndexed_withOHLC_percentageChange.to_excel("quoteDataIndexed_withOHLC_percentageChange.xlsx", index=False)


	#IPO FILTER
	tradingDays = len(df_quoteDataIndexed_withOHLC_percentageChange)

	if tradingDays == 0:
		finalReport = [symbol, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		print(symbol)
		print("symbol is a new IPO, no calculated data for the first trading day.")
		return(finalReport)
	else:
		#Calculate standard deviation
		windowCapture = period
	
		slice_df = df_quoteDataIndexed_withOHLC_percentageChange.iloc[:, 7:23] #column8->23: O1->C4
		#print(slice_df)

		import numpy as np

		def excel_like_std(window_df):
			return np.std(window_df.values.flatten(), ddof=1)

		stdDev_rolling = (
	    	slice_df
	    	.rolling(window=windowCapture, min_periods=windowCapture)
	    	.apply(
	        	lambda x: excel_like_std(slice_df.loc[x.index]),
	        	raw=False
	    	)
	    	.iloc[:, 0]   # 👈 collapse DataFrame → Series
		)

		df_quoteDataIndexed_withOHLC_percentageChange["stdDev_rolling"] = stdDev_rolling
		#print(df_quoteDataIndexed_withOHLC_percentageChange["std_rolling_10"].head())
		#df_quoteDataIndexed_withOHLC_percentageChange.to_excel("checkStdDevRolling.xlsx", index=False)

		#Sigma Results
		SigmaReturns = []
		for row in df_quoteDataIndexed_withOHLC_percentageChange.itertuples():
			if row[26] == 0:
				pass
			elif row[26] != 0:
				SigmaReturns.append({
					"date": row[2],
					"min": round(row[24], 4),
					"max": round(row[25], 4),
					"stdDev": round(row[26], 4),
					"sigmaDown": round(row[24]/row[26], 2),
					"sigmaUp": round(row[25]/row[26], 2),
					})
	
		df_SigmaReturns=pd.DataFrame(SigmaReturns)

		signalsUpCount = (df_SigmaReturns['sigmaUp'] > 2).sum()
		signalsDownCount = (df_SigmaReturns['sigmaDown'] < -2).sum()
		print(f"as of {len(df_SigmaReturns)} trading days:")
		print(f" {signalsUpCount} signals - Up")
		print(f" {signalsDownCount} signals - Down")
		signalsCount = signalsUpCount + signalsDownCount

		if signalsCount > 0:
			eHDs = round(len(df_SigmaReturns)/signalsCount, 2)
		else:
			eHDs = 5

		print(f" expected holding days: {eHDs}")

		if len(SigmaReturns) > 5:
			#the day 1 (the last recent trading day = today)
			symbol_SigmaReturns = SigmaReturns[-1]	#the last trading date (today)
			symbol_sigmaUp = symbol_SigmaReturns['sigmaUp']
			symbol_sigmaDown = symbol_SigmaReturns['sigmaDown']
			symbol_stdDev = symbol_SigmaReturns['stdDev']
			#the previous day 2
			smrD2 = SigmaReturns[-2]				
			smrD2_smUp = smrD2['sigmaUp']
			smrD2_smDown = smrD2['sigmaDown']
			smrD2_stdDev = smrD2['stdDev']
			#the previous day 3
			smrD3 = SigmaReturns[-3]				
			smrD3_smUp = smrD3['sigmaUp']
			smrD3_smDown = smrD3['sigmaDown']
			smrD3_stdDev = smrD3['stdDev']
			#the previous day 4
			smrD4 = SigmaReturns[-4]				
			smrD4_smUp = smrD4['sigmaUp']
			smrD4_smDown = smrD4['sigmaDown']
			smrD4_stdDev = smrD4['stdDev']
			#the previous day 5
			smrD5 = SigmaReturns[-5]				
			smrD5_smUp = smrD5['sigmaUp']
			smrD5_smDown = smrD5['sigmaDown']
			smrD5_stdDev = smrD5['stdDev']

			finalReport = [
			symbol, symbol_sigmaUp, symbol_sigmaDown, symbol_stdDev,
			smrD2_smUp, smrD2_smDown,smrD2_stdDev,
			smrD3_smUp, smrD3_smDown,smrD3_stdDev,
			smrD4_smUp, smrD4_smDown,smrD4_stdDev,
			smrD5_smUp, smrD5_smDown,smrD5_stdDev,
			eHDs,
			]
			print(f"{symbol} today sigma Up: {symbol_sigmaUp}")
			return(finalReport)
		else:
			finalReport = [symbol, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
			print(symbol)
			print("symbol is traded less than 5 trading days. this market is new")
			return(finalReport)


period = 11

#pick a list of stocks that need to be computed
#==============================================
symbols = symbolListSet		#TCBS List
print("using TCBS marketlist for Sigma calculation\n")
#symbols = marketListSet	#VNstock List

#Test List
#symbols = ["FPT", "FRT", "HPG", "VIC", "VHM", "VNM", "TCB", "BID", "GAS", "GVR", "MBB"]
#symbols =["FPT","AAN"]

#control API requests
import time
import random

REQUESTS_PER_MINUTE = random.randint(10, 40)
INTERVAL = 60 / REQUESTS_PER_MINUTE
TodaySigma = []
next_run = time.time()

#calculating Sigmas
for symbol in symbols:

	result = Sigma(symbol, period)

	TodaySigma.append({
		"symbol": symbol,
		"sigmaUp": result[1],
		"sigmaDown": result[2],
		"1stdDev": result[3],
		"D2U": result[4],
		"D2D": result[5],
		"D2stdDev": result[6],
		"D3U": result[7],
		"D3D": result[8],
		"D3stdDev": result[9],
		"D4U": result[10],
		"D4D": result[11],
		"D4stdDev": result[12],
		"D5U": result[13],
		"D5D": result[14],
		"D5stdDev": result[15],
		"eHDs": result[16]
	})

	# counting
	length = len(symbols)
	count = symbols.index(symbol) + 1	

	# control API request rate
	next_run += INTERVAL
	sleep_time = next_run - time.time()

	print(f"{symbol} | buffer {max(0, sleep_time):.2f}s")
	print(f"{count} on {length} finished\n")

	if sleep_time > 0:
		time.sleep(sleep_time)

df_TodaySigma = pd.DataFrame(TodaySigma)
df_TodaySigma.to_excel("Excel_SIG.xlsx", index=False)
print("SIG is rendered successfully!\n")


#====================================================================
# WLR Calculation
#================

SignalsList = []	#SigmaUp > 2
for row in df_TodaySigma.itertuples():
	if row[2] > 2:
		SignalsList.append(row[1])
print("today signals: ")
print(SignalsList)
print("\n")

# Write to txt file
with open("_today_SIGNALS.txt", "w", encoding="utf-8") as f:
    f.write(", ".join(SignalsList))
print("Printed Signal List to txt file!")

# using intraday data source from TCBS
def WLR_TCBS(symbol):
	# numbers of trades stats
	#========================
	data = client.get_price_history(symbol)
	total = data['total']
	headIndex = total - 1
	#print(total)

	page_Q100 = math.ceil(total/100)-1
	#print(page_Q100)

	size_odd = total - page_Q100*100
	#print(size_odd)

	#last100Trade = client.get_price_history(symbol, page = 0, size=100)['data']
	#first100Trade = client.get_price_history(symbol, page = page, size=100)['data']

	size_odd = client.get_price_history(symbol, page = 0, size=size_odd)['data']
	df_size_odd = pd.DataFrame(size_odd)
	#print(df_size_odd)

	#market is traded less than 100 trades
	#=====================================
	if page_Q100 == 0:
		Trades = len(df_size_odd)
		count_positive = (df_size_odd['pcp'] > 0).sum()
		count_negative = (df_size_odd['pcp'] < 0).sum()
		expectedRatio = count_positive/count_negative

		Us = count_positive
		Ds = count_negative
		UDR = expectedRatio

		Result = [symbol, Trades, Us, Ds, UDR]
		print("less than 100 up-pushed trades, WLR calculation done for " + str(symbol))
		return(Result)

	#market is traded more than 100 trades
	#=====================================
	else:
		Q100 = []

		import time

		for i in range(0,page_Q100):
			start = time.time()

			slice100 = client.get_price_history(symbol, page = i, size=100)['data']
			df_slice100 = pd.DataFrame(slice100)
			Q100.append(df_slice100)

			elapsed = time.time() - start
			time.sleep(max(0, 1 - elapsed))

		Q100final = pd.concat(Q100, ignore_index=True)

		df_Merged = pd.concat([df_size_odd, Q100final], ignore_index=True)
		#print(len(df_Merged))
		#print(df_Merged)
		#df_Merged.to_excel("Trades.xlsx", index=False)

		count_positive = (df_Merged['pcp'] > 0).sum()
		count_negative = (df_Merged['pcp'] < 0).sum()
		expectedRatio = count_positive/count_negative

		#print(count_positive)
		#print(count_negative)
		#print(expectedRatio)

		#lastRecentTrade = client.get_price_history(symbol, page = 0, size=1)['data']
		#print(lastRecentTrade)

		Trades = len(df_Merged)
		Us = count_positive
		Ds = count_negative
		UDR = expectedRatio

		Result = [symbol, Trades, Us, Ds, UDR]
		print("more than 100 up-pushed trades, WLR calculation done for " + str(symbol))
		return(Result)

WLR_Report_TCBS = []

for symbol in SignalsList:

	totalWork = len(SignalsList)
	work = SignalsList.index(symbol) + 1

	WLR_Report_TCBS.append(WLR_TCBS(symbol))

	print(f"{work} on {totalWork} finished\n")

df_WLR_TCBS = pd.DataFrame(WLR_Report_TCBS)
df_WLR_TCBS.to_excel("Excel_WLR_TCBS.xlsx", index=False)
print(df_WLR_TCBS)
print("WLR report is rendered successfully!\n")

# Write to txt file
confirmationWLR = "WLR printed to Excel"
with open("_today_WLR.txt", "w", encoding="utf-8") as f:
    f.write(", ".join(confirmationWLR))
print("Printed WLR confirmation to txt file!")


#====================================================================
# Show Confirmation
import tkinter as tk
from tkinter import messagebox

def confirm_popup(message):
    root = tk.Tk()
    root.withdraw()  # hide main window
    messagebox.showinfo("Confirmation", message)
    root.destroy()

if len(df_TodaySigma) > 0:
	confirm_popup("SIGNALS and WLRs are generated successfully!")

import time
time.sleep(600)   # pause for 10 mins 