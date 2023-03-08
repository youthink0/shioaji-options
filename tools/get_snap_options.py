# %%
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

import tools.globals as globals

MAX_FLOAT_VALUE = float('inf') # float最大值



# %%
def get_next_wednesday(today):
    """
    Get next week's number in this month.
    
    :param: today (datetime.date)

    :return: nextwed (int)
    """
    oneday = datetime.timedelta(days = 1)
    while today.weekday() != 2: # 2 mean Wednesday
        today += oneday
    nextwed = today
    return nextwed

# %%
def get_opt_txnum(date):
    """
    Get prefix(TX?) symbol code for today's week option.
    
    :param: date (datetime.date)

    :return: res (str)
    """
    endday=get_next_wednesday(date)
    beginday=get_next_wednesday(datetime.date(endday.year, endday.month, 1))
    begin = int(beginday.strftime("%W"))
    end = int(endday.strftime("%W"))

    week=end - begin + 1 
    if week == 3: # no W3, instead is month expiration
        res='TXO'
    else:
        res='TX'+str(week)
    return res

# %%
def get_option_code(cp):
    """
    Get final two symbol code for whole week option.
    
    :param: cp (str)

    :return: option_code (str)
    """
    if(datetime.datetime.now().weekday()!=2): # not wednesday
        now = get_next_wednesday(datetime.datetime.now())
    else:
        now = datetime.datetime.now()
    month = now.month
    year = now.year

    month_to_code = '0ABCDEFGHIJKL'
    if cp=="P":
        month_to_code = '0MNOPQRSTUVWX'

    option_code = month_to_code[month]
    option_code += str(year%10)
    
    return option_code

# %%
def makebound(input,cbr):
    """
    Get every Option strike price, input is market now, and cbr is gap from each strike price.
    
    :param: input (int)
    :param: cbr (int)
    :return:  (tuple)
    """
    c='['+str(cbr*int(input/cbr))+'-'+str(cbr*int(input/cbr)+cbr)+')'
    return (cbr*int(input/cbr),str(cbr*int(input/cbr)+cbr),c)

# %%
def get_tse_bound(upper,bottom,txname):
    """
    Get all strike prices base on upper and bottom price.
    
    :global param: api
    :param: upper (int)
    :param: bottom (int)
    :return:  (tuple): (int, str, str)
    """

    putcode=get_option_code("P")
    callcode=get_option_code("C")

    contract_snap = globals.api.snapshots([globals.api.Contracts.Indexs.TSE.TSE001])[0]
    close=contract_snap.close # get TSE001's current market price 
    upc=close+upper
    botc=close+bottom 
    bt=makebound(botc,50)[0]
    up=makebound(upc,50)[0]
    contract_code_list=[ txname+str(_)+putcode for _ in range(bt,up+50,50)]
    contract_code_list+=[ txname+str(_)+callcode for _ in range(bt,up+50,50)]
    return contract_code_list

# %%
def get_snap_options():
    """
    Get 當時所有options的snapshot資訊.
    並assign到相應之global變數
    
    :global param: lastcontractprice
    :global param: txo_weekly_dict
    :global param: api
    :return:  None
    """

    contractname=get_opt_txnum(datetime.datetime.today())
    contracts=globals.api.Contracts.Options[contractname] # get whole contract available on market
    code_list=get_tse_bound(2000,-2000,contractname) # get specifc contracts depend on parameter limit
    
    for contract in contracts:
        if contract.code in code_list:
            try:
                contract_snap = globals.api.snapshots([contract])[0]
                if globals.txo_weekly_dict.get(contract.code[:-2]) is None:
                    globals.txo_weekly_dict[contract.code[:-2]] = {'C':None,'P':None}
                data={
                    'askprice':contract_snap.sell_price, #賣方第一檔
                    'bidprice':contract_snap.buy_price, #買方第一檔
                    'close':contract_snap.close,
                    'snap': contract_snap,
                    'contract':contract # 商品合約物件
                }
                globals.txo_weekly_dict[contract.code[:-2]][contract.symbol[-1]]=data # 把同一檔的call跟put資訊放進同一個dict中
                globals.lastcontractprice[contract.code]=data
            except Exception as e:
                print(e)
                print("error")

# %%
def get_at_the_money_info():
    """
    找到指定時間之當時的價平點數及檔位
    並assign到相應之global變數

    :global param: txo_weekly_dict
    :global param: at_the_money_code
    :global_param: at_the_money
    
    :return: None
    """
    txo_weekly_key = list(globals.txo_weekly_dict.keys()) #拿到dict的key
    globals.at_the_money_code = ""
    globals.at_the_money = MAX_FLOAT_VALUE
    for keys in txo_weekly_key:
        strike_code = globals.txo_weekly_dict[keys] #得到dict中的第一個key的value(型別為一個dict)
        if strike_code['C'].get('close') != 0.0 and strike_code['P'].get('close') != 0.0 :
            strike_money = strike_code['C'].get('close') + strike_code['P'].get('close') #得到價平
        else:
            strike_money = MAX_FLOAT_VALUE

        if strike_money < globals.at_the_money:
            globals.at_the_money_code = keys
            globals.at_the_money = strike_money


# %%
def update_at_the_money_price(cp, askbid):
    """
    此func是為了更新globals.txo_weekly_dict
    
    :param: cp (str)
    :param: askbid (str)
    :global param: txo_weekly_dict
    :global param: at_the_money_code

    return: none
    """
    get_snap_options() 
    price = globals.txo_weekly_dict[globals.at_the_money_code][cp].get(askbid)
    return price

# %%
