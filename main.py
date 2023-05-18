# %%
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import importlib
import time
import datetime
import json
import threading
from threading import Event

import shioaji as sj
import login.shioaji_login as shioaji_login
from shioaji import BidAskFOPv1
importlib.reload(shioaji_login)

import tools.globals as globals
import tools.get_snap_options as snap
import tools.message_log as message_log
import tools.get_simulate_positions as positions
import tools.cover as cover
import tools.contract as contract

# %%
def update_config():
    """
    Threading function.
    每秒更新config相關參數
    
    :global param: get_simulation_time
    :global param: simulation_mode
    :global param: simulation_optionright
    :global param: simulation_quantity
    :global param: simulation_action

    :global param: get_cover_time
    :global param: cover_put_strike
    :global param: cover_call_strike
    :global param: cover_quantity

    :return: None
    """

    pre_get_simulation_time = None
    pre_simulation_mode = None
    pre_simulation_optionright = None
    pre_simulation_quantity = None
    pre_simulation_action = None

    pre_get_cover_time = None 
    pre_cover_mode = None
    pre_cover_put_strike = None 
    pre_cover_call_strike = None 
    pre_cover_quantity = None
    pre_cover_gap_time = None

    pre_sell_call_quantity = None
    pre_buy_call_quantity = None
    pre_buy_call_price = None

    while(True):

        with open('config.json') as f:
            config_data = json.load(f)

            globals.get_simulation_time =  datetime.datetime.strptime(config_data['get_simulation_time'], '%H:%M:%S').time()
            globals.get_cover_time =  datetime.datetime.strptime(config_data['get_cover_time'], '%H:%M:%S').time()

            ### set simulation ###
            if config_data['simulation_mode'].lower() == "false":
                globals.simulation_mode = False
            else:
                globals.simulation_mode = True

            if config_data['simulation_optionright'].lower() == "c":
                globals.simulation_optionright = 'C'
            else:
                globals.simulation_optionright = 'P'

            if config_data['simulation_action'].lower() == "buy":
                globals.simulation_action = 'Buy'
            else:
                globals.simulation_action = 'Sell'

            globals.simulation_quantity = config_data['simulation_quantity']
            
            ### set cover ###
            if config_data['cover_mode'].lower() == "false":
                globals.cover_mode = False
            else:
                globals.cover_mode = True

            globals.cover_put_strike = config_data['cover_put_strike']
            globals.cover_call_strike = config_data['cover_call_strike']
            globals.cover_quantity = config_data['cover_quantity']
            globals.cover_gap_time = config_data['cover_gap_time']
            globals.sell_call_quantity = config_data['sell_call_quantity']
            globals.buy_call_quantity = config_data['buy_call_quantity']
            globals.buy_call_price = config_data['buy_call_price']

            ### detect ###
            if(pre_get_simulation_time != globals.get_simulation_time):
                print(f'Get simulation time has been set to {globals.get_simulation_time}')
                pre_get_simulation_time = globals.get_simulation_time

            if(pre_simulation_mode != globals.simulation_mode):
                print(f'Simulation_mode has been set to {globals.simulation_mode}')
                pre_simulation_mode = globals.simulation_mode

            if(pre_simulation_optionright != globals.simulation_optionright):
                print(f'Simulation_optionright has been set to {globals.simulation_optionright}')
                pre_simulation_optionright = globals.simulation_optionright

            if(pre_simulation_action != globals.simulation_action):
                print(f'Simulation_action has been set to {globals.simulation_action}')
                pre_simulation_action = globals.simulation_action

            if(pre_simulation_quantity != globals.simulation_quantity):
                print(f'Simulation_quantity has been set to {globals.simulation_quantity}')
                pre_simulation_quantity = globals.simulation_quantity

            if(pre_get_cover_time != globals.get_cover_time):
                print(f'Get cover time has been set to {globals.get_cover_time}')
                pre_get_cover_time = globals.get_cover_time

            if(pre_cover_mode != globals.cover_mode):
                print(f'Cover mode has been set to {globals.cover_mode}')
                pre_cover_mode = globals.cover_mode

            if(pre_cover_put_strike != globals.cover_put_strike):
                print(f'Cover put strike has been set to {globals.cover_put_strike}')
                pre_cover_put_strike = globals.cover_put_strike

            if(pre_cover_call_strike != globals.cover_call_strike):
                print(f'Cover call strike has been set to {globals.cover_call_strike}')
                pre_cover_call_strike = globals.cover_call_strike

            if(pre_cover_quantity != globals.cover_quantity):
                print(f'Cover quantity has been set to {globals.cover_quantity}')
                pre_cover_quantity = globals.cover_quantity

            if(pre_cover_gap_time != globals.cover_gap_time):
                print(f'Cover gap time has been set to {globals.cover_gap_time}')
                pre_cover_gap_time = globals.cover_gap_time

            if(pre_sell_call_quantity != globals.sell_call_quantity):
                print(f'Sell call quantity has been set to {globals.sell_call_quantity}')
                pre_sell_call_quantity = globals.sell_call_quantity

            if(pre_buy_call_quantity != globals.buy_call_quantity):
                print(f'Buy call quantity has been set to {globals.buy_call_quantity}')
                pre_buy_call_quantity = globals.buy_call_quantity
            
            if(pre_buy_call_price != globals.buy_call_price):
                print(f'Buy call price has been set to {globals.buy_call_price}')
                pre_buy_call_price = globals.buy_call_price

            time.sleep(1)



# %%
def update_snap_options():
    """
    Threading function.
    每秒偵測,若現在時間符合get_simulation_time, 則找尋當下價平 
    且若simulation_mode為True則下模擬單
    
    :global param: get_simulation_time
    :global param: simulation_mode
    :return: None
    """

    while(True): 
        now = datetime.datetime.now()
        
        if(now.time().replace(microsecond=0) == globals.get_simulation_time):
            if globals.simulation_mode:
                snap.get_snap_options()
                snap.get_at_the_money_info()
                print(globals.get_simulation_time, "時刻之價平和檔位及成交點數和: ", globals.at_the_money_code, globals.at_the_money)
                
                option_code = globals.at_the_money_code +  snap.get_option_code(globals.simulation_optionright)
                globals.contract = contract.fill_contract(option_code)
                positions.place_simulate_order(globals.simulation_quantity, option_code, globals.simulation_optionright, globals.simulation_action)

        time.sleep(1)

# %%
def detect_cover_time():
    """
    Threading function.
    每秒偵測,判斷現在時間符合get_cover_time 符合則交付cover控制
    且若simulation_mode為True則下模擬單
    
    :global param: get_cover_time
    :return: None
    """
    while(True): 
        now = datetime.datetime.now()
        
        if(now.time().replace(microsecond=0) == globals.get_cover_time):
            log_msg = f"A cover time been detected. time: {globals.get_cover_time}\n"
            print(log_msg)
            message_log.write_log(log_msg)
            cover.cover_controller()
        time.sleep(1)

# %%
def price_checker():
    """
    每隔15秒會偵測一次最新價平 當目前價平模擬單之成交價虧損達1.4倍則平倉出場
    :global param: positions (list)
    :return: None
    """
    while(True):
        for p in globals.positions:
            if(p[0] == 1):
                askbid = 'bidprice' #要平倉現有買進倉位 因此找最佳賣價
                cover_action = sj.constant.Action.Sell
            elif(p[0] == -1):
                askbid = 'askprice' #要平倉現有賣出倉位 因此找最佳買價
                cover_action = sj.constant.Action.Buy
            

            if(p[3] == 1):
                cp = 'C'
            elif(p[3] == -1):
                cp = 'P'
                
            price = snap.update_at_the_money_price(cp, askbid)
            condition1 = p[0] == 1 and price <= p[2]*(1/1.4)
            condition2 = p[0] == -1 and price >= p[2]*1.4

            if(condition1 or condition2):
                log_msg = f"A loss stop has been detected. Strike code: {p[4]}, Market price: {price}, buy price: {p[2]}\n"
                print(log_msg)
                message_log.write_log(log_msg)
                # cover.cover_controller()
                cover.place_simulate_cover_order(p[1], p[4], cp, cover_action) #p[1]: 口數， p[3]: optionright, p[4]: option_code

        time.sleep(15)
        

# %%
def load_position():
    # 取得Position 
    globals.position = globals.api.list_positions(globals.api.futopt_account)

    if len(globals.position) == 0:
        print("None")

# %%
def limit_sell_call_order():
    """
    每日開盤前，掛最接近台灣指數收盤的履約價N口sell call漲停價，N由globals.sell_call_quatity決定

    漲停價說明: 假設昨日收盤15000，則今天掛sell call 15000 價格在15000*10% = 1500上

    :global param: sell_call_quantity
    :global param: api
    :return:  None
    """

    cover_day = datetime.datetime.today()
    contractname = snap.get_opt_txnum(cover_day)

    contract_snap = globals.api.snapshots([globals.api.Contracts.Indexs.TSE.TSE001])[0]
    close=contract_snap.close # get TSE001's current market price 

    # Get proper close strike price
    close_div = int(close / 100) * 100
    close_mod = close % 100
    if close_mod >= 0 and close_mod < 25:
        close = close_div
    elif close_mod >= 25 and close_mod <75:
        close = close_div + 50
    else:
        close = close_div + 100

    price = int(close / 100) * 10 #為了讓下單價格的尾數為0，實現10點一跳

    cover_call_code = contractname + str(close) + snap.get_option_code("C")

    daily_limit_contract = contract.fill_contract(cover_call_code)
    order = globals.api.Order(
            action=sj.constant.Action.Sell,
            price=price, # strike_price * 10%, and let price be 10 point as one jump
            quantity=globals.sell_call_quantity, # 根據config.json的口數
            price_type=sj.constant.StockPriceType.LMT, #MKT: 市價 LMT: 限價
            order_type=sj.constant.FuturesOrderType.ROD, # 當日有效
            octype=sj.constant.FuturesOCType.Auto, #倉別，設定成自動
            OptionRight=sj.constant.OptionRight.Call, #選擇權類型
            account=globals.api.futopt_account #下單帳戶指定期貨帳戶
        )

    trade = globals.api.place_order(daily_limit_contract, order)
    print('***')
    log_msg = f'A daily sell call limit order {trade} is already sent!\n'
    print(log_msg)
    message_log.write_log(log_msg)
    print('***\n')

# %%
def limit_buy_call_order():
    """
    每日開盤前，掛最接近台灣指數收盤的履約價N口buy call跌停價，N由globals.buy_call_quatity決定
    成交價則由globals.buy_call_price決定

    :global param: buy_call_quantity
    :global param: buy_call_price
    :global param: api
    :return:  None
    """

    cover_day = datetime.datetime.today()
    contractname = snap.get_opt_txnum(cover_day)

    contract_snap = globals.api.snapshots([globals.api.Contracts.Indexs.TSE.TSE001])[0]
    close=contract_snap.close # get TSE001's current market price 
    close = int(close - close/10)

    # Get proper close strike price
    close_div = int(close / 100) * 100
    close_mod = close % 100
    if close_mod >= 0 and close_mod < 50:
        close = close_div + 200
    else:
        close = close_div + 300

    cover_call_code = contractname + str(close) + snap.get_option_code("C")

    daily_limit_contract = contract.fill_contract(cover_call_code)
    order = globals.api.Order(
            action=sj.constant.Action.Buy,
            price=globals.buy_call_price, # strike_price * 10%, and let price be 10 point as one jump
            quantity=globals.buy_call_quantity, # 根據config.json的口數
            price_type=sj.constant.StockPriceType.LMT, #MKT: 市價 LMT: 限價
            order_type=sj.constant.FuturesOrderType.ROD, # 當日有效
            octype=sj.constant.FuturesOCType.Auto, #倉別，設定成自動
            OptionRight=sj.constant.OptionRight.Call, #選擇權類型
            account=globals.api.futopt_account #下單帳戶指定期貨帳戶
        )

    trade = globals.api.place_order(daily_limit_contract, order)
    print('***')
    log_msg = f'A daily buy call limit order {trade} is already sent!\n'
    print(log_msg)
    message_log.write_log(log_msg)
    print('***\n')

# %%
def main():
    """
    Controlled whole program, make app execute.
    
    :global param: api
    """
    # initialize all global variables
    globals.initialize()

    # load_position()
    pickle_p = positions.read_position()
    if pickle_p != []:
        if len(pickle_p) == 1:
            globals.positions = [positions.read_position()] #讀取上次執行還未平倉之模擬倉位
        else:
            globals.positions = positions.read_position()
            
    # log in
    globals.api = shioaji_login.login()
    globals.api.set_order_callback(positions.place_cb)

    snap.get_snap_options()
    snap.get_at_the_money_info()
    print("程式始執行之價平和檔位及成交點數和: ", globals.at_the_money_code, globals.at_the_money)

    # Start update config thread. All config variable will be updated every second.
    update_config_thread = threading.Thread(target = update_config)
    update_config_thread.start()
    time.sleep(0.6)

    update_snap_options_thread = threading.Thread(target = update_snap_options)
    update_snap_options_thread.start()
    time.sleep(0.6)

    detect_cover_time_thread = threading.Thread(target = detect_cover_time)
    detect_cover_time_thread.start()

    time.sleep(1)
    price_checker_thread = threading.Thread(target = price_checker)
    price_checker_thread.start()
    
    ### 在開盤前預掛前日最接近台灣指數(TSE)收盤價之Sell call漲停單
    limit_sell_call_order()
    time.sleep(1)
    limit_buy_call_order()

    ### 訂閱平倉檔次之bidask ###
    cover_call_code, cover_put_code = cover.get_cover_code()
    print("put: ", cover_put_code, "call: ", cover_call_code)
    cover.subscribe_cover_code(cover_call_code, cover_put_code)
    
    # print(api.Contracts.Options.TX4)



# %%
if __name__ == "__main__":
    main() 

# %%
globals.txo_weekly_dict[globals.at_the_money_code][globals.simulation_optionright]

# %%
cover_day = datetime.datetime.today()
contractname = snap.get_opt_txnum(cover_day)

contract_snap = globals.api.snapshots([globals.api.Contracts.Indexs.TSE.TSE001])[0]
close=contract_snap.close # get TSE001's current market price 
close

# %%
# 目前實現進度: 
# 1. 在get_simulation_time抓到價平後下模擬單，並在達到停損條件後(a. 成交價 or b. 強制平倉時間)出掉 * b.Done * a. Done
# 2. 做最佳移動掛單 *已完成在cover.dynamic_price_adjustment Done
# 3. 完成模擬下單 * Done
# 4. cover那邊加一個控制參數 * Done
# 5. 可以儲存上次倉位 * Done
# 6. 實單也能偵測到成交價停損條件
# 7. 實單平倉 改成IOC後要改一下THREAD的架構 然後當CALL跟PUT都平倉成功就終止程式 * Done

### 細節補充 ###
# 實單方面 口數是CALL PUT共用
# 實單方面的平倉 只要考慮平倉買進就好 因此沒有設ACTION參數
# 不論實單或模擬單 皆沒有考慮禮拜三下單狀況
# 研究一下lastcontractprice的內部資訊是甚麼 沒用就註明一下
# config.json裡 只能有一方是true 當有true則有另一方一定要false 這樣訊息才不會太混亂


