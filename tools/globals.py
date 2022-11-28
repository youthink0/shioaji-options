#!/usr/bin/env python
# coding: utf-8


def initialize():
    ### config setting ###
    global get_strike_time

    get_strike_time = None

    ### interior setting ###
    global api
    global lastcontractprice, txo_weekly_dict
    global at_the_money_code, at_the_money 
    
    api = None
    lastcontractprice={} #最新的各檔報價資訊
    txo_weekly_dict={} #key為每檔之code， value則為該檔之call put資訊，
    at_the_money_code = "" #價平code
    at_the_money = 0 #價平和