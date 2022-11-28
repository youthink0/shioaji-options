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
    lastcontractprice={}
    txo_weekly_dict={}
    at_the_money_code = ""
    at_the_money = 0