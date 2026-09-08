# MAKE PUSH - PULL ORDERS

# This engine will update the bid/ask of pending orders to bid1/ask1 so the order can be filled
#==============================================================================================
import os
import pandas as pd


# AUTHENTICATION
#====================================
from tcbs import TCBSClient
import TCBS_ACC

from dotenv import load_dotenv
load_dotenv(r"D:/API/API_KEYS.env")
TCBS_API_KEY = os.getenv("TCBS_API_KEY")
client = TCBSClient(api_key=TCBS_API_KEY)

# ACCOUNT DEFINITION
#===================
accountMargin = TCBS_ACC.TCBS_ACC.Margin
accountNormal = TCBS_ACC.TCBS_ACC.Normal
accountDerivative = TCBS_ACC.TCBS_ACC.Derivative

# CONFIG ==================================================
import random
modes = [1,2]
mode = random.choice(modes)
print(f"Mode: {mode}")

if mode == 1:
    account = accountMargin
    print("Checking for Margin account:")
    loggingMessage = "Script started - Margin Account"
elif mode == 2:
    account = accountNormal
    print("Checking for Cash account:")
    loggingMessage = "Script started - Cash Account"


# LOGGING =================================================
import logging
logging.basicConfig(
    filename="_task_log_MPP.txt",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.info(loggingMessage)


#=======================================================================================
# 1. Get pending filled order
#=============================
orderbook = client.get_order_book(account_no=account)['data']
df_orderbook = pd.DataFrame(orderbook, columns = ['symbol','execType','orderQtty','execQtty','remainQtty','quotePrice','matchPrice','orStatus','orderID', 'orderQtty','limitPrice','quotePrice'])
#df_orderbook.to_excel("df_orderbook.xlsx", index=False)
print("orderbook:")
print(df_orderbook)

# order Status
#=============
# A = editting
# 2 = awaiting
# 3 = cancelled
# 4 = partially matched
# 8 = order placed
# 10 = editted
# 12 = fully matched

pendingFills = []
for row in df_orderbook.itertuples():
    if str(row[8]) == "A":
        continue
    if int(row[8]) == 4:
        pendingFills.append({
            "symbol": row[1],
            "side": row[2],
            "order ID": row[9],
            "orderQtty": row[10],
            "limitPrice": row[11],
            "quotePrice": row[12]
            })
    if int(row[8]) == 2:
        pendingFills.append({
            "symbol": row[1],
            "side": row[2],
            "order ID": row[9],
            "orderQtty": row[10],
            "limitPrice": row[11],
            "quotePrice": row[12]
            })

#print(pendingFills)
df_pendingFills = pd.DataFrame(pendingFills)
print("pending fills: ")
print(df_pendingFills)


#======================================================================================
# 2. GET Last matched, bis1/ask1 pair
#====================================
LTP = client.get_market_info(index=1)['data']
df_LTP = pd.DataFrame(LTP)

marketInfo = pd.DataFrame(LTP, columns = ['symbol','matchPrice','bidPrice01','offerPrice01'])
#print(marketInfo)

infoBidAsk = []
for row in marketInfo.itertuples():
    infoBidAsk.append({
        "symbol": row[1],
        "bid1": row[3],
        "ask1": row[4]
        })
#print(infoBidAsk)


#==============================================
# Merging 2 list and prepare for order updating
# combine 2 lists (orderbook + marketprice)
#==============================================
if df_pendingFills.empty:
    pass
    print("no action needs to be taken")
    #df_listCombined = pd.merge(df_pendingFills, marketInfo)
    action = 0
else:
    print("\nthere are orders have been placed")
    df_listCombined = pd.merge(df_pendingFills, marketInfo)  #merging 2 panda DataFrame
    action = 1
    print(df_listCombined)
    #df_listCombined.to_excel("orderUpdating.xlsx", index=False)


#==================================================================
# 3. Updating existing order
#===========================
# NB will be updated with bid1
# NS will be updated with ask1
# row[2]: AS = Awaiting Sell, AB = Awaiting Buy

#print(action)
if action == 0:
    pass
else:
    for row in df_listCombined.itertuples():
        
        symbol = row[1]
        side = row[2]
        orderID = row[3]
        quantity = row[4]
        limitPrice = row[5]
        bidPrice1 = row[8]
        askPrice1 = row[9]

        # --- update the sell side ---
        if side == "NS":

            if int(limitPrice) > int(askPrice1):
                print(f"updated sell order for: {symbol}, at price: {askPrice1}")
                client.update_order(account, orderID, price=askPrice1, quantity=quantity)
        
        if side == "AS":

            if int(limitPrice) > int(askPrice1):
                print(f"updated sell order for: {symbol}, at price: {askPrice1}")
                client.update_order(account, orderID, price=askPrice1, quantity=quantity)
        
        # --- update the buy side ---
        if side == "NB":

            if int(limitPrice) < int(bidPrice1):
                print(f"updated buy order for: {symbol}, at price: {bidPrice1}")
                client.update_order(account, orderID, price=bidPrice1, quantity=quantity)
        
        if side == "AB":
            
            if int(limitPrice) < int(bidPrice1):
                print(f"updated buy order for: {symbol}, at price: {bidPrice1}")
                client.update_order(account, orderID, price=bidPrice1, quantity=quantity)


import time
time.sleep(1)   # pause for 10 seconds