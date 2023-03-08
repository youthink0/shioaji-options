#!/usr/bin/env python
# coding: utf-8


def initialize():
    ### config setting ###
    global get_simulation_time #下價平模擬單的時間
    global simulation_mode, simulation_optionright, simulation_quantity, simulation_action #模擬單資訊
    global get_cover_time #強制平倉的時間
    global cover_mode, cover_put_strike, cover_call_strike, cover_quantity, cover_gap_time #實單平倉資訊
    global sell_call_quantity #開盤下漲停價之口數

    get_simulation_time = None
    simulation_mode = simulation_optionright = simulation_quantity = simulation_action = None
    get_cover_time = None
    cover_mode = cover_put_strike = cover_call_strike = cover_quantity = cover_gap_time = None
    sell_call_quantity = None

    ### interior setting ###
    global api
    global lastcontractprice, txo_weekly_dict
    global at_the_money_code, at_the_money 
    global positions, contract
    global third_best_call_buy_price, third_best_call_sell_price
    global third_best_put_buy_price, third_best_put_sell_price
    global cover_call_contract, cover_put_contract
    
    api = None
    lastcontractprice={} #最新的各檔報價資訊
    txo_weekly_dict={} #key為每檔之code， value則為該檔之call put資訊，
    at_the_money_code = "" #價平code
    at_the_money = 0 #價平和
    positions = [] #倉位
    contract = None #目前價平之指定CP資訊
    third_best_call_buy_price = third_best_call_sell_price = None # call第三檔之最佳買賣價
    third_best_put_buy_price = third_best_put_sell_price = None # put第三檔之最佳買賣價
    cover_call_contract = cover_put_contract = None #平倉call put之指定CP資訊