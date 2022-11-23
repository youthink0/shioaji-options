import datetime
lastcontractprice={}
TXO_weekly_dict={}


def getNextWEDNESDAY(today):
    oneday = datetime.timedelta(days = 1)
    while today.weekday() != 2:
        today += oneday
    nextwed = today
    return nextwed

def get_opt_TXnum(date):
    endday=getNextWEDNESDAY(date)
    beginday=getNextWEDNESDAY(datetime.date(endday.year, endday.month, 1))
    begin = int(beginday.strftime("%W"))
    end = int(endday.strftime("%W"))

    week=end - begin + 1 
    if week == 3:
        res='TXO'
    else:
        res='TX'+str(week)
    return res


def getweekopt():
    for item in api.Contracts.Options.keys():
        if item == get_opt_TXnum(datetime.datetime.today()):
            return api.Contracts.Options[item]
    return None

def get_option_code(cp):
    
    if(datetime.datetime.now().weekday()!=2):
        now = getNextWEDNESDAY(datetime.datetime.now())
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

def makebound(input,cbr):
    c='['+str(cbr*int(input/cbr))+'-'+str(cbr*int(input/cbr)+cbr)+')'
    return (cbr*int(input/cbr),str(cbr*int(input/cbr)+cbr),c)


def get_tse_bound(upper,bottom,txname):
    putcode=get_option_code("P")
    callcode=get_option_code("C")

    contract_snap = api.snapshots([api.Contracts.Indexs.TSE.TSE001])[0]
    close=contract_snap.close
    upc=close+upper
    botc=close+bottom
    bt=makebound(botc,50)[0]
    up=makebound(upc,50)[0]
    contract_code_list=[ txname+str(_)+putcode for _ in range(bt,up+50,50)]
    contract_code_list+=[ txname+str(_)+callcode for _ in range(bt,up+50,50)]
    return contract_code_list

def getsnapOptions():
    global lastcontractprice

    contractname=get_opt_TXnum(datetime.datetime.today())
    contracts=api.Contracts.Options[contractname]
    k=0
    code_list=get_tse_bound(2000,-2000,contractname)
    for contract in contracts:
        if contract.code in code_list:
            try:
                contract_snap = api.snapshots([contract])[0]
                if TXO_weekly_dict.get(contract.code[:-2]) is None:
                    TXO_weekly_dict[contract.code[:-2]] = {'C':None,'P':None}
                data={
                    'askprice':contract_snap.sell_price, #賣方第一檔
                    'bidprice':contract_snap.buy_price, #買方第一檔
                    'close':contract_snap.close,
                    'snap': contract_snap,
                    'contract':contract # 商品合約物件 範例如下
                }
                TXO_weekly_dict[contract.code[:-2]][contract.symbol[-1]]=data
                lastcontractprice[contract.code]=data
                k+=1
            except Exception as e:
                print(e)
                print("error")
