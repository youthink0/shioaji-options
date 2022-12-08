# %%
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import importlib
import time
import datetime

import shioaji as sj
import login.shioaji_login as shioaji_login
from shioaji import BidAskFOPv1
# from shioaji.constant import Action, OptionRight, StockPriceType, FuturesOrderType, FuturesOCType #選擇權下單，多匯入一個OptionRight常數
importlib.reload(shioaji_login)

import tools.globals as globals
import tools.get_snap_options as snap
import tools.contract as contract

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
def judge_symbol(code, price):
    month_to_code = '0ABCDEFGHIJKL'
    if cp=="P":
        month_to_code = '0MNOPQRSTUVWX'

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

    """
    globals.cover_put_contract = contract.fill_contract(cover_put_code)
    globals.api.quote.subscribe(
        globals.cover_put_contract,
        quote_type = sj.constant.QuoteType.BidAsk, # or 'bidask'
        version = sj.constant.QuoteVersion.v1, # or 'v1'
    )
    """

    @globals.api.on_bidask_fop_v1()
    def quote_callback(exchange:sj.Exchange, bidask:BidAskFOPv1):
        #always avoid making calulations inside the callback function.
        """
        Quoting subscribe function. It is called every tick(theoretically)
        """
        #print("ask_price: ", bidask['ask_price'], "bid_price: ", bidask['bid_price'])

        # 取第三檔掛單價格，是為了避免夜盤時價差太大可能造成的風險
        globals.third_best_buy_price = bidask['ask_price'][2] # 第三檔之最佳買價
        globals.third_best_sell_price = bidask['bid_price'][2] # 第三檔之最佳賣價

        time.sleep(5)

# %%
def dynamic_price_adjustment(trade, price):
    return


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

    snap.get_snap_options() # 呼叫此func是為了更新globals.txo_weekly_dict
    price = globals.txo_weekly_dict[globals.at_the_money_code][cp].get(askbid)
    
    send_test_msg(
            int(price) ,
            quantity,
            action,
            code= option_code,
            delivery_month= globals.contract['delivery_month'],
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
        contract = globals.cover_call_contract #選擇權Contract
        optionright = sj.constant.OptionRight.Call
        price = globals.third_best_buy_price #價格
        order = globals.api.Order(
            action=sj.constant.Action.Buy,
            price=price,
            quantity=globals.cover_quantity, #口數
            price_type=sj.constant.StockPriceType.LMT, #MKT: 市價 LMT: 限價
            order_type=sj.constant.FuturesOrderType.ROD,
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

        dynamic_price_adjustment(trade, price)
    
    if globals.simulation_mode:
        ### 下模擬單平倉 ###
        option_code = globals.at_the_money_code +  snap.get_option_code(globals.simulation_optionright)
        for p in globals.positions:
            if(p[0] == 1):
                cover_action = sj.constant.Action.Sell
            elif(p[0] == -1):
                cover_action = sj.constant.Action.Buy
            place_simulate_cover_order(p[1], option_code, p[3], cover_action) #p[1]: 口數， p[3]: optionright

    time.sleep(1)