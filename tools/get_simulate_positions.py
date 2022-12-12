# %%
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import time
import pickle

import shioaji as sj

import tools.globals as globals
import tools.message_log as message_log

# %%
def place_cb(stat, msg):
    """
    Called every time an order or a deal has been detected.
    
    :global param: msg_list ()

    return: none
    """
    if(stat == sj.constant.OrderState.FDeal):
        print('A deal has been detected.')
        print(f'Deal information: code:{msg["code"]}, action:{msg["action"]}, price:{msg["price"]}, quantity:{msg["quantity"]}, optionright:{msg["optionright"]}')
        print(f'Delivery month:{msg["delivery_month"]}, security type: {msg["security_type"]}')
        message_log.write_log('stat: ' + stat + ' msg: ' + json.dumps(msg, ensure_ascii=False) + '\n' )
        fill_positions(msg)

# %%
def fill_positions(deal):
    """
    紀錄模擬下單之倉位

    :global param positions: (list)
    
    :return: None
    """
    
    '''
    # First check if the type and month match the tracking future.
    if(
        deal['code'] != globals.contract['code'] or
        deal['delivery_month'] != globals.contract['delivery_month'] or
        deal['optionright'] != globals.contract['option_right'] or
        deal["security_type"] != 'OPT'
      ):
        print("This deal is not as same as the future currently tracking.")
        return
    '''
    
    price = int(deal['price'])
    quantity = int(deal['quantity'])
    code = deal['code']
    try:
        if(deal['action'] == 'Buy'):
            action = 1
        elif(deal['action'] == 'Sell'):
            action = -1
        else:
            raise ValueError('The action of this deal is neither "Buy" nor "Sell".')
    except ValueError as err:
        traceback.print_exc()

    if(action == 1):
        action_text = "Buy"
    else:
        action_text = "Sell"

    try:
        if(deal['optionright'] == 'C'):
            optionright = 1
        elif(deal['optionright'] == 'P'):
            optionright = -1
        else:
            raise ValueError('The optionright of this deal is neither "Call" nor "Put".')
    except ValueError as err:
        traceback.print_exc()
    
    if(optionright == 1):
        action_text += " Call"
    else:
        action_text += " Put"
    
    # While there are still some positions and it is the oppsite of the deal:
    ori_quantity = quantity
    while(globals.positions and globals.positions[0][0] == -action and globals.positions[0][3] == optionright and quantity > 0):
        
        if(globals.positions[0][1] > quantity):
            globals.positions[0][1] -= quantity
            quantity = 0
            # The deal has been recorded, exit the function
            break
        else:
            quantity -= globals.positions[0][1]

            print('***')
            log_msg = f'A position with {globals.positions[0]} has been covered!\n'
            print(log_msg)
            message_log.write_log(log_msg)
            print('***')
            del globals.positions[0]
            
    
    if (quantity > 0):
        
        # Ensure the data type is int
        position = [action, int(quantity), int(price), int(optionright), code, False]
        
        if(action == 1):
            globals.positions.append(position)
            globals.positions = sorted(globals.positions, key=lambda p: p[2], reverse=False)
        else:
            globals.positions.append(position)
            globals.positions = sorted(globals.positions, key=lambda p: p[2], reverse=True)
        
        #print("current positions: ", globals.positions[0])
        #[action, int(quantity), int(price), int(price), False]
        print('***')
        log_msg = f'A position with code={code}, type={action_text}, quantity={quantity}, price={price} has been added to the track list!\n'
        print(log_msg)
        message_log.write_log(log_msg)
        print('***')

    store_position(globals.positions)
    

# %%
def send_test_msg(
    price,
    quantity,
    action,
    code,
    delivery_month,
    optionright,
    stat=sj.constant.OrderState.FDeal,
    security_type='OPT'
):
    """
    For test purpose.
    """
    # Testing with msg

    msg = {}
    msg['price'] = price
    msg['quantity'] = quantity
    msg['action'] = action
    msg['code'] = code
    msg['delivery_month'] = delivery_month
    msg['optionright'] = optionright
    msg["security_type"] = security_type

    place_cb(stat, msg)

# %%
def place_simulate_order(quantity, option_code, cp = 'C', action = sj.constant.Action.Buy):
    """
    依照JSON檔支模擬下單參數 送出立即成交之模擬單
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
# stat為FOrder 已經送出委託
# stat為FDeal 已經完全成交或部分成交

# %%
def read_position():
    """
    讀取外部存取之上次程式模擬倉位

    return: stored_position (list)
    """
    with open('positions.pickle', 'rb') as f:
        try:
            stored_position = pickle.load(f)
        except EOFError:
            stored_position = []
    time.sleep(1)
    
    return stored_position

# %%
def store_position(position):
    """
    存取目前模擬倉位至外部檔案

    return: None
    """
    with open('positions.pickle', 'wb') as f:
        pickle.dump(position, f)   
    time.sleep(2)
