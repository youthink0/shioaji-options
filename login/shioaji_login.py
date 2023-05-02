import json
import threading
import os
import shioaji as sj

from pathlib import Path

def login():
    """
    Login with account info specify in the file 'account_info.json'.
    :return: shioaji api.
    """

    account_info = 'login/account/account_info.json'
    
    with open(account_info, newline='') as jsonfile:
        account_data = json.load(jsonfile)
        
    ca_path = account_data['ca_path']
    ca_name = account_data['ca_name']
    ca_path = ca_path + ca_name
    #ca_path = os.path.abspath(ca_path)

    api = sj.Shioaji() 
    # api_login = api.login(
    #     api_key="8iS351Teaj7bJk9RFJZdeLbg7h9fPAzPSYzA8z9tT1Yg",     # 請修改此處
    #     secret_key="9FBDD72PypmrsxpUJzBTVtFyiVyb2et7XE2sWzmfL2RH"
    # )
    
    api_login = api.login(
        person_id = account_data['person_id'],
        passwd = account_data['passwd'], 
        #contracts_cb=lambda security_type: print(f"{repr(security_type)} fetch done.")
    )
    
    print(f'Login with ID {account_data["person_id"]}')
    print(f'Login status: {api_login}')
    
    activate = api.activate_ca(ca_path=ca_path, ca_passwd=account_data['ca_passwd'], person_id=account_data['person_id'])

    if(activate):
        print(f'Activating CA at the path {ca_path}')
        print('\n')
    else:
        print(f'Failed! Can not activate CA at the path {ca_path}')
        print('\n')
    
    return api