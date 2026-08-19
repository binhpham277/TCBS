# MARKET PRICE LEVELS
# ===========================================================================

import pandas as pd
import os
import math
import time
from dotenv import load_dotenv

# AUTHENTICATION
#==========================================
from vnstock import register_user
load_dotenv(r"D:/API/API_KEYS.env")
VNSTOCK_API_KEY = os.getenv("VNSTOCK_API_KEY")
register_user(VNSTOCK_API_KEY)

from tcbs import TCBSClient
import TCBS_ACC

from dotenv import load_dotenv
load_dotenv(r"D:/API/API_KEYS.env")
TCBS_API_KEY = os.getenv("TCBS_API_KEY")
client = TCBSClient(api_key=TCBS_API_KEY)



# CONFIG
# ============================================================================

look_back = 100
sigma_period = 11



# FUNCTIONS DEFINITION
# ============================================================================

def getData(symbol, period):
    from datetime import date, timedelta
    
    backdate = 0

    endDate = date.today() - timedelta(days=backdate)
    print(endDate)
    startDate = endDate - timedelta(days=int(period))
    endDate_str = str(endDate)
    startDate_str = str(startDate)

    sym = str(symbol)

    days = period
    lengthQ =f"{days}D"

    from vnstock import Quote
    quote = Quote(symbol=sym)
    df_quote = quote.history(end=endDate_str, length=lengthQ, interval="1D")

    return(df_quote)   #return a DataFrame


def cluster_levels(prices, tolerance=0.01):
    prices = sorted(prices)

    clusters = []

    for price in prices:
        if not clusters:
            clusters.append([price])
            continue

        center = sum(clusters[-1]) / len(clusters[-1])

        if abs(price - center) / center <= tolerance:
            clusters[-1].append(price)
        else:
            clusters.append([price])

    return [
        {
            "level": sum(cluster) / len(cluster),
            "touches": len(cluster),
            "prices": cluster
        }
        for cluster in clusters
    ]


def key_levels_up(symbol, lookback, sigma_period):

    print(f"Calculating key price levels for: {symbol}")

    df_market = getData(symbol, look_back)
    #print(df_market)

    average_p = df_market.loc[df_market.index[-1], ["open", "high", "low", "close"]].mean()
    print(f"average price: {average_p}\n")

    df_price_o = df_market["open"].tolist()
    df_price_h = df_market["high"].tolist()
    df_price_l = df_market["low"].tolist()
    df_price_c = df_market["close"].tolist()

    prices_ohlc = df_price_o + df_price_h + df_price_l + df_price_c

    cluster_market = cluster_levels(prices_ohlc, tolerance = 0.01)
    df_cluster = pd.DataFrame(cluster_market)

    df_cluster["above_avg"] = df_cluster["prices"].apply(lambda x: [v for v in x if v >= average_p])
    df_cluster["below_avg"] = df_cluster["prices"].apply(lambda x: [v for v in x if v < average_p])
    #print("cluster table:")
    #print(df_cluster)

    key_levels = df_cluster["level"].tolist()
    up_levels = [key_level for key_level in key_levels if key_level >= average_p]
    do_levels = [key_level for key_level in key_levels if key_level < average_p]

    print("Above levels (raw):")
    print(up_levels)
    print("Below levels (raw):")
    print(do_levels)

    # Pick 6 values and filling up for empty levels

    up_levels_standardized = (up_levels[:6] + [0] * 6)[:6]
    do_levels_standardized = (do_levels[-6:] + [0] * 6)[:6]
    print("\n")
    print("Above key levels (standardized):")
    print(up_levels_standardized)
    print("Below key levels (standardized):")
    print(do_levels_standardized)

    uk0 = round(up_levels_standardized[0], 4)
    uk1 = round(up_levels_standardized[1], 4)
    uk2 = round(up_levels_standardized[2], 4)
    uk3 = round(up_levels_standardized[3], 4)
    uk4 = round(up_levels_standardized[4], 4)
    uk5 = round(up_levels_standardized[5], 4)

    dk0 = round(do_levels_standardized[0], 4)
    dk1 = round(do_levels_standardized[1], 4)
    dk2 = round(do_levels_standardized[2], 4)
    dk3 = round(do_levels_standardized[3], 4)
    dk4 = round(do_levels_standardized[4], 4)
    dk5 = round(do_levels_standardized[5], 4)

    key_levels_report = [symbol, uk0, uk1, uk2, uk3, uk4, uk5, dk0, dk1, dk2, dk3, dk4, dk5]
    print("\nkey levels report:")
    print(key_levels_report)


    # Calculate key price levels with standard deviation
    # indexing data for later calculation
    quoteDataIndexed = []
    for row in df_market.itertuples():
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
        #return(finalReport)
    else:
        #Calculate standard deviation
        windowCapture = sigma_period

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
    #print(df_SigmaReturns)
    stdDev = df_SigmaReturns.iloc[-1]["stdDev"]
    print(f"\nCurrent standard deviation: {stdDev}")
    

    uk0_s = round((average_p * (1+stdDev) ** 1), 4)
    uk1_s = round((average_p * (1+stdDev) ** 2), 4)
    uk2_s = round((average_p * (1+stdDev) ** 3), 4)
    uk3_s = round((average_p * (1+stdDev) ** 4), 4)
    uk4_s = round((average_p * (1+stdDev) ** 5), 4)
    uk5_s = round((average_p * (1+stdDev) ** 6), 4)

    dk0_s = round((average_p * (1-stdDev) ** 1), 4)
    dk1_s = round((average_p * (1-stdDev) ** 2), 4)
    dk2_s = round((average_p * (1-stdDev) ** 3), 4)
    dk3_s = round((average_p * (1-stdDev) ** 4), 4)
    dk4_s = round((average_p * (1-stdDev) ** 5), 4)
    dk5_s = round((average_p * (1-stdDev) ** 6), 4)

    print("\nUp levels with std Dev:")
    print(uk0_s)
    print(uk1_s)
    print(uk2_s)
    print(uk3_s)
    print(uk4_s)
    print(uk5_s)

    print("\nDown levels with std Dev:")
    print(dk0_s)
    print(dk1_s)
    print(dk2_s)
    print(dk3_s)
    print(dk4_s)
    print(dk5_s)

    list_Up_data = [uk0, uk1, uk2, uk3, uk4, uk5]
    list_Up_stdDev = [uk0_s, uk1_s, uk2_s, uk3_s, uk4_s, uk5_s]

    list_Down_data = [dk0, dk1, dk2, dk3, dk4, dk5]
    list_Down_stdDev = [dk0_s, dk1_s, dk2_s, dk3_s, dk4_s, dk5_s]

    list_Up_data.sort()
    list_Up_stdDev.sort()

    list_Down_data.sort(reverse=True)
    list_Down_stdDev.sort(reverse=True)

    print(list_Up_data)
    print(list_Up_stdDev)
    print(list_Down_data)
    print(list_Down_stdDev)

    list_up = [a if a != 0 else b for a, b in zip(list_Up_data, list_Up_stdDev)]
    list_down = [a if a != 0 else b for a, b in zip(list_Down_data, list_Down_stdDev)]

    list_up.sort()
    list_down.sort(reverse=True)


    print("\nkey price levels UP:")
    print(list_up)
    print("\nkey price levels DOWN:")
    print(list_down)

    print("\npair ratio:")
    print(list_up[0])
    print(list_up[1])
    print(list_up[2])
    print(list_up[3])
    print(list_up[4])
    print(list_up[5])

    print(list_down[0])
    print(list_down[1])
    print(list_down[2])
    print(list_down[3])
    print(list_down[4])
    print(list_down[5])

    wlr_1 = (list_up[0] - average_p) / (average_p - list_down[0])
    wlr_2 = (list_up[1] - average_p) / (average_p - list_down[1])
    wlr_3 = (list_up[2] - average_p) / (average_p - list_down[2])
    wlr_4 = (list_up[3] - average_p) / (average_p - list_down[3])
    wlr_5 = (list_up[4] - average_p) / (average_p - list_down[4])
    wlr_6 = (list_up[5] - average_p) / (average_p - list_down[5])

    print(f"WLR 1: {wlr_1}")
    print(f"WLR 2: {wlr_2}")
    print(f"WLR 3: {wlr_3}")
    print(f"WLR 4: {wlr_4}")
    print(f"WLR 5: {wlr_5}")
    print(f"WLR 6: {wlr_6}")

    pair_ratio = sum([wlr_2, wlr_3, wlr_4, wlr_5, wlr_6]) / 5
    print(f"pair ratio average: {round(pair_ratio, 4)}")

    report_up = [symbol, list_up[0], list_up[1], list_up[2], list_up[3], list_up[4], list_up[5]]
    print("\nFINAL REPORT FOR UP PRICE LEVELS:")
    print(report_up)
    print("\n")
    return(report_up)


# =================================================================================
# Generate MPL (MARKET PRICE LEVELS)

# TCBS List (HOSE)
marketList = client.get_market_info(index=1)['data']
allMarketList = pd.DataFrame(marketList, columns = ['symbol','totalVal'])
symbolsList = []
for row in allMarketList.itertuples():
    if row[2] > 0:
        symbolsList.append(row[1])
symbolListSet = list(set(symbolsList))
print(str(len(symbolListSet)) + " tickers for tcbs list\n")


# Symbol List
symbols = symbolListSet     #TCBS List
print("using TCBS marketlist for MPL calculation\n")

# Test List
#symbols = ["FPT", "FRT", "HPG", "VIC", "VHM", "VNM", "TCB", "BID", "GAS", "GVR", "MBB"]


# ==============================================
# control API requests
import time
import random
REQUESTS_PER_MINUTE = random.randint(10, 40)
INTERVAL = 60 / REQUESTS_PER_MINUTE
next_run = time.time()

TodayMPL = []

# calculating MPL
for symbol in symbols:

    result = key_levels_up(symbol, look_back, sigma_period)

    TodayMPL.append({
        "symbol": symbol,
        "L1": result[1],
        "L2": result[2],
        "L3": result[3],
        "L4": result[4],
        "L5": result[5],
        "L6": result[6],
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

df_TodayMPL = pd.DataFrame(TodayMPL)
df_TodayMPL.to_excel("Excel_MPL.xlsx", index=False)
print("MPL is rendered successfully!\n")