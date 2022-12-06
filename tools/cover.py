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

def judge_symbol(code, price):
    month_to_code = '0ABCDEFGHIJKL'
    if cp=="P":
        month_to_code = '0MNOPQRSTUVWX'

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
        print("ask_price: ", bidask['ask_price'], "bid_price: ", bidask['bid_price'])

        # 取第三檔掛單價格，是為了避免夜盤時價差太大可能造成的風險
        globals.third_best_buy_price = bidask['ask_price'][2] # 第三檔之最佳買價
        globals.third_best_sell_price = bidask['bid_price'][2] # 第三檔之最佳買賣價

        time.sleep(5)