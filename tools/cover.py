# %%
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import importlib
import time
import datetime
import pandas as pd

import shioaji as sj
import login.shioaji_login as shioaji_login
from shioaji import BidAskFOPv1
importlib.reload(shioaji_login)

import tools.globals as globals
import tools.get_snap_options as snap
import tools.contract as contract
import tools.get_simulate_positions as positions
import tools.message_log as message_log

# %%
def get_cover_code():
    """
    依照get_cover_time之指定平倉時間，得到平倉call, put代碼

    :global param: globals.get_cover_time
    :global param: globals.cover_put_strike
    :global param: globals.cover_call_strike

    :return: cover_call_code, cover_put_code (str, str)
    """
    if globals.get_cover_time > datetime.time(0, 0) and globals.get_cover_time < datetime.time(5, 1):
        cover_day = datetime.datetime.today() + datetime.timedelta(days=1)
        contractname = snap.get_opt_txnum(cover_day)
    else:
        cover_day = datetime.datetime.today()
        contractname = snap.get_opt_txnum(cover_day)

    cover_put_code = contractname + str(globals.cover_put_strike) + snap.get_option_code("P")
    cover_call_code = contractname + str(globals.cover_call_strike) + snap.get_option_code("C")

    return cover_call_code, cover_put_code

# %%
def judge_symbol(code, bidask):
    """
    判斷目前訂閱發送之價格屬於call or put的實單合約
    
    
    :param: cp (str)
    :global param: api
    :global param: cover_call_contract
    :global param: cover_put_contract
    :global param: third_best_buy_price

    return: none
    """
    call_month_symbol = '0ABCDEFGHIJKL'
    put_month_symbol = '0MNOPQRSTUVWX'
    if code[-2:-1] in call_month_symbol:
        # 取第三檔掛單價格，是為了避免夜盤時價差太大可能造成的風險
        globals.third_best_call_buy_price = bidask['ask_price'][2] # 第三檔之最佳買價
        globals.third_best_call_sell_price = bidask['bid_price'][2] # 第三檔之最佳賣價
    elif code[-2:-1] in put_month_symbol:
        globals.third_best_put_buy_price = bidask['ask_price'][2] # 第三檔之最佳買價
        globals.third_best_put_sell_price = bidask['bid_price'][2] # 第三檔之最佳賣價
    # print("call price: ", globals.third_best_call_buy_price, "put price: ", globals.third_best_put_buy_price)
        

# %%
def get_trade(cp):
    """
    得到json檔中call put各自的trade資訊 每次只平倉一口
    
    :param: cp (str)
    :global param: api
    :global param: cover_call_contract
    :global param: cover_put_contract
    :global param: third_best_buy_price

    return: none
    """
    if cp == 'C':
        contract = globals.cover_call_contract
        optionright = sj.constant.OptionRight.Call
        price = globals.third_best_call_buy_price
    elif cp == 'P':
        contract = globals.cover_put_contract
        optionright = sj.constant.OptionRight.Put
        price = globals.third_best_put_buy_price
    else:
        return None
    order = globals.api.Order(
        action=sj.constant.Action.Buy,
        price=price,
        # quantity=globals.cover_quantity, #口數
        quantity=1, #口數
        price_type=sj.constant.StockPriceType.LMT, #MKT: 市價 LMT: 限價
        order_type=sj.constant.FuturesOrderType.IOC, # 立即成交否則取消
        octype=sj.constant.FuturesOCType.Cover, #倉別，收盤時平倉
        OptionRight=optionright, #選擇權類型
        account=globals.api.futopt_account #下單帳戶指定期貨帳戶
    )

    trade = globals.api.place_order(contract, order)
    print('***')
    log_msg = f'An cover order {trade} is already sent!\n'
    print(log_msg)
    message_log.write_log(log_msg)
    print('***\n')

    return trade, price

# %%
def dynamic_price_adjustment():
    """
    實單平倉之買進價格為動態調整 每隔json指定之間隔秒數會偵測一次最新買價並送出平倉單 永遠掛在最佳買價上
    
    :param: trade (<class 'shioaji.order.Trade'>)
    :param: price (int)
    :global param: api
    :global param: third_best_buy_price
    :global param: cover_gap_time

    return: none
    """
    call_price = put_price = 0
    while(True): 
        if call_price != globals.third_best_call_buy_price and globals.third_best_call_buy_price != None:
            call_trade, call_price = get_trade('C')

            
            log_msg = f'An cover call order price is already update to {call_price}!\n'
            print(log_msg)
            message_log.write_log(log_msg)
            
        if put_price != globals.third_best_put_buy_price and globals.third_best_put_buy_price != None:
            put_trade, put_price = get_trade('P')

            log_msg = f'An cover put order price is already update to {put_price}!\n'
            print(log_msg)
            message_log.write_log(log_msg)
            
        positions = globals.api.get_account_openposition(account=globals.api.futopt_account)
        df_positions = pd.DataFrame(positions.data())
        if df_positions.empty:
            print('***')
            log_msg = f'No more open position in account now!\n'
            print(log_msg)
            message_log.write_log(log_msg)
            print('***\n')
            break
            
        time.sleep(globals.cover_gap_time)

# %%
def place_simulate_cover_order(quantity, option_code, cp, action):
    """
    依照JSON檔支模擬下單參數 送出立即成交之平倉模擬單
    assign globlas.contract
    
    :param: quantity (int)
    :param: cp (str)
    "param: action (sj.constant.Action.Buy or sj.constant.Action.Sell)
    :global param: txo_weekly_dict
    :global param: at_the_money_code
    :global param: contract

    return: none
    """
    
    if action == "Buy":
        askbid = 'askprice'
    else:
        askbid = 'bidprice'

    if cp == "C":
        optionright = sj.constant.OptionRight.Call #選擇權類型
    else:
        optionright = sj.constant.OptionRight.Put

    price = snap.update_at_the_money_price(cp, askbid)
    
    positions.send_test_msg(
            int(price) ,
            quantity,
            action,
            code= option_code,
            delivery_month= "Test",
            optionright= optionright, 
            stat= sj.constant.OrderState.FDeal,
            security_type= 'OPT'
    )
    
def cover_controller():
    """
    若cover_mode成立則執行實單平倉:
        json設定之平倉時間一到，便依照C、P設定之檔次及口數，下平倉，限價在第三跳
    若simulation_mode成立則執行模擬平倉交易:
        依照position裡目前價平合約執行平倉
    # 步驟
    # 取得帳戶資訊
    # 確立合約
    # 確立order
    # 送出order

    :return: None
    """

    # globals.position = globals.api.list_positions(globals.api.futopt_account)
    # Offset.CLOSE: A closing offset (CO) order is a limit order that is executed at market close but can be placed anytime during the trading day. 
    if globals.cover_mode:
        ### 下實單平倉 ###
        dynamic_price_adjustment()
        
    if globals.simulation_mode:
        ### 下模擬單平倉 ###
        while(globals.positions):
            for p in globals.positions:
                if(p[0] == 1):
                    cover_action = sj.constant.Action.Sell
                elif(p[0] == -1):
                    cover_action = sj.constant.Action.Buy

                if(p[3] == 1):
                    cp = 'C'
                elif(p[3] == -1):
                    cp = 'P'
                place_simulate_cover_order(p[1], p[4], cp, cover_action) #p[1]: 口數， p[3]: optionright, p[4]: option_code       

    time.sleep(1)

# %%
def subscribe_cover_code(cover_call_code, cover_put_code):
    """
    訂閱平倉call, put之bidask，即時得到第三跳的報價

    :global param: globals.cover_call_contract
    :global param: globals.cover_put_contract
    :global param: third_best_buy_price (int)
    :global param: third_best_sell_price (int)

    :return: None
    """

    globals.cover_call_contract = contract.fill_contract(cover_call_code)
    globals.api.quote.subscribe(
        globals.cover_call_contract,
        quote_type = sj.constant.QuoteType.BidAsk, # or 'bidask'
        version = sj.constant.QuoteVersion.v1, # or 'v1'
    )

    
    globals.cover_put_contract = contract.fill_contract(cover_put_code)
    globals.api.quote.subscribe(
        globals.cover_put_contract,
        quote_type = sj.constant.QuoteType.BidAsk, # or 'bidask'
        version = sj.constant.QuoteVersion.v1, # or 'v1'
    )

    @globals.api.on_bidask_fop_v1()
    def quote_callback(exchange:sj.Exchange, bidask:BidAskFOPv1):
        #always avoid making calulations inside the callback function.
        """
        Quoting subscribe function. It is called every tick(theoretically)
        """
        #print("ask_price: ", bidask['ask_price'], "bid_price: ", bidask['bid_price'])
        judge_symbol(bidask['code'], bidask)