import sys
sys.path.append('../data')
sys.path.append('../msg')
import net,json,time
import sendmsg
from decimal import *

###############################################################################################
# 开盘啦
###############################################################################################
#KPL_RUL = 'https://pchis.kaipanla.com/w1/api/index.php'
KPL_RUL = 'https://pchq.kaipanla.com/w1/api/index.php'
KPL_SIGN_TIME = 0
def kpldog():
    global KPL_RUL
    param = {}
    param['a'] = 'GetPointPlate'
    param['c'] = 'PCArrangeData'
    param['Index'] = '0'
    param['PointType'] = '1,2,3'
    param['st'] = '1'
    #param['Date'] = '2018-07-30'#time.strftime("%Y-%m-%d", time.localtime())#
    param['Token'] = '2efa906af1b5641270b21845a4bea7c0'
    param['UserID'] = '228432'
    res = net.sendpost(KPL_RUL,param)
    if res != -1:
        try:
            data = json.loads(res)
        except Exception as ee:
            print("[kpl] dog json error")
            return -1
        global KPL_SIGN_TIME
        for row in data['content']['List']:
            tid = row['Time']
            if tid <= KPL_SIGN_TIME:
                continue
            KPL_SIGN_TIME = tid
            comment = row['Comment']
            stock = row['Stock']
            for stk in stock:
                name = stk[1]
                tip = '[' + name + ',' + stk[0] + ',' + str(stk[2]) + '%]'
                comment = comment.replace(name,tip)

            time_local = time.localtime(tid)
            stime = time.strftime("%H:%M:%S", time_local)
            msg = '[开盘啦][' + stime + '] ' + comment
            #print(msg)
            sendmsg.add(msg)




KPL_ZLJE_LIST = [] #开盘啦主力净额列表
def kplje():
    global KPL_RUL
    param = {}
    param['a'] = 'RealRankingInfo'
    param['c'] = 'StockRanking'
    param['Ratio'] = '5'
    param['Type'] = '1'
    param['Index'] = '0'
    param['Order'] = '1'
    param['st'] = '50'
    param['Token'] = '2efa906af1b5641270b21845a4bea7c0'
    param['UserID'] = '228432'
    res = net.sendpost(KPL_RUL,param)
    if res != -1:
        try:
            data = json.loads(res)
        except Exception as ee:
            print("[kpl] je json error")
            return -1

        global KPL_ZLJE_LIST
        if data['errcode'] == '1001':
            print("[kpl] je login error")
            return -1

        #print(data['list'])
        for row in data['list']:
            code = row['Code']
            if code in KPL_ZLJE_LIST:
                continue

            ZLJE = row['ZLJE']
            jz = Decimal(ZLJE / 100000000).quantize(Decimal('0.00'))
            jz = '{:g}'.format(float(jz))
            jz = float(jz)
            if jz > 2:
                msg = '[主力净额][' + time.strftime("%H:%M:%S", time.localtime()) + '] ' + row['Name'] + ' ' + code + ' 本日净流入' + str(jz) + '亿'
                #print(msg)
                sendmsg.add(msg)
                KPL_ZLJE_LIST.append(code)


def update():
    kpldog()
    kplje()
