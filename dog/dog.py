import pymysql,sys
sys.path.append('../data')
sys.path.append('../tool')
sys.path.append('../msg')
import tools,net
import sendmsg

############################################################
##逻辑处理
GP_CATCH_DIC = {}                       # 股票缓存字典
BK_CATCH_DIC = {}                       # 个股对应版块缓存字典
BK_NAME_CATCH_DIC = {}                  # 版块名称缓存字典
#TIP_CATCH_LIST = []                     # 消息缓存列表
############################################################

#盘中看盘狗
# TODO
# 1.多线程发送协议,运行策略与请求数据分别进行
# 2.未开板新股去除判定
'''数据结构
   [0]名字 [1]今日开盘价  [2]昨日收盘价 [3]当前价格
   [4]今日最高价 [5]今日最低价 [6]竞买价，即“买一”报价
   [7]竞卖价，即“卖一”报价 [8]成交的股票数，由于股票交易以一百股为基本单位，所以在使用时，通常把该值除以一百
   [9]成交金额，单位为“元”，为了一目了然，通常以“万元”为成交金额的单位，所以通常把该值除以一万
   [10]买一申请4695股，即47手  [11]买一报价  [12]买二申请 [13]买二报价
   [14]买三申请  [15]买三报价  [16]买四申请  [17]买四报价  [18]买五申请
   [19]买五报价  [20]卖一申报3100股，即31手  [21]卖一报价
   [22]卖二申请  [23]卖二报价  [24]卖三申请  [25]卖三报价  [26]卖四申请  [27]卖四报价  [28]卖五申请 [29]卖五报价
   [30]日期  [31]时间
'''
def dog():
    stockmax = 33
    stock_name, stock_open, stock_lastclose, stock_price, stock_date, stock_time = 0, 1, 2, 3, 30, 31
    global GP_ALL_STR_URL_LIST,GP_CATCH_DIC
    for url in GP_ALL_STR_URL_LIST:
        res = net.send(url, 0, 0)
        if res == -1:
            print('[dog] dog net res err')
            continue

        stocks =(' ' + res).split(';')
        for val in stocks:
            code = val[14:][:6]
            stock = val[21:][:-1].split(',')
            if len(stock) != stockmax:
                #print('[dog] stock data err ' + str(stockmax))
                #print(stock)
                continue

            stocklist = GP_CATCH_DIC[code]['list']

            ############
            # 数据处理 #
            ############
            # 1)重复数据
            if len(stocklist) > 0 and stocklist[stock_time] == stock[stock_time]:
                continue
            # 2)停盘
            if float(stock[stock_price]) == 0:
                continue
            # 3)构建通用数据
            if len(stocklist) == 0:
                buildStockData(stock,code)

            # 4)清除保存数据
            stock[stock_name] = None
            stock[stock_open] = None
            stock[stock_date] = None
            stock[stock_lastclose] = None

            # 5)缓存数据
            GP_CATCH_DIC[code]['list'] = stock

            ############
            # 策略处理 #
            ############
            # 1)快速拉升/快速跳水
            quickup(code)

            # 2)首次涨到X%
            #firstup(code)

            # 3)涨跌停
            limitup(code)

            # 4)新高
            #highup(code)

            # 5)平台突破
            #platformup(code)

    # sendmsg
    #TIP_CATCH_LIST

def buildStockData(stock,code):
    stock_name,stock_open,stock_lastclose,stock_date = 0,1,2,30
    data = {}
    data['name'] = stock[stock_name]
    data['open'] = float(stock[stock_open])
    data['date'] = stock[stock_date]
    data['lastclose'] = float(stock[stock_lastclose])
    data['st'] = stock[stock_name].find('ST') >= 0
    data['last'] = []
    global GP_CATCH_DIC
    GP_CATCH_DIC[code] = data


#快速拉升3%以上
def quickup(code):
    stock_price,stock_time = 3,31
    global GP_CATCH_DIC
    data = GP_CATCH_DIC[code]
    stock = data['list']
    lastprice = data['last']            # 上次价格
    curprice = float(stock[stock_price])       # 当前价格
    lastprice.append(curprice)

    lastlen = len(lastprice)
    if lastlen < 3:
        #数据太少无法计算
        return
    elif lastlen > 10:
        #只存储10个数据
        del lastprice[0]

    #快速拉升
    minprice = float(min(lastprice))
    if minprice <= 0:
        print('[dog] minprice err')
        #print(data)
        return
    global BK_NAME_CATCH_DIC    #TIP_CATCH_LIST
    percent = float((curprice - minprice) / minprice * 100)
    #print('percent:' + str(percent) + '  curprice:' + str(curprice) + '   minprice:' + str(minprice))
    if percent >= 3:
        msg = '[拉升][' + stock[stock_time] + '] ' + data['name'] + ' ' + code + ' ' + BK_NAME_CATCH_DIC[code] + ' 快速拉升' + str(percent) + '%'
        #TIP_CATCH_LIST.append(msg)
        sendmsg.add(msg)
        lastprice.clear()
        return

    #快速跳水
    maxprice = float(max(lastprice))
    if maxprice <= 0:
        print('[dog] maxprice err')
        #print(data)
        return
    percent = float((maxprice - curprice) / curprice * 100)
    if percent >= 3:
        msg = '[跳水][' + stock[stock_time] + '] ' + data['name'] + ' ' + code + ' ' + BK_NAME_CATCH_DIC[code] + ' 快速跳水' + str(percent) + '%'
        #TIP_CATCH_LIST.append(msg)
        lastprice.clear()
        sendmsg.add(msg)


#首次涨到3%
FIRSTUP_OLD_TIP = []          #首次提示记录
def firstup(code):
    global FIRSTUP_OLD_TIP
    if code in FIRSTUP_OLD_TIP:
        return
    percent = 3                             #3%
    stock_high,stock_time = 4,31
    global GP_CATCH_DIC
    data = GP_CATCH_DIC[code]
    stock = data['list']
    close = float(data['lastclose'])        #昨日收盘价
    high = float(stock[stock_high])         #今日最高价
    price = tools.getpercent(close,percent)
    if high >= price:
        FIRSTUP_OLD_TIP.append(code)
        msg = '[涨幅][' + stock[stock_time] + '] ' + data['name'] + ' ' + code + ' 首次涨幅到3% ' + BK_NAME_CATCH_DIC[code]
        #TIP_CATCH_LIST.append(msg)
        sendmsg.add(msg)


#涨停跌停
GP_ZT_LIST = []                         #涨停列表
GP_DT_LIST = []                         #跌停列表
#GP_LB_LIST = {}                         #连板列表
def limitup(code):
    stock_price,stock_time = 3,31
    global GP_CATCH_DIC,GP_ZT_LIST,GP_DT_LIST  #GP_CHECK_ZT_LIST,GP_DT_CNT,GP_ZT_CNT,GP_ZT_LIST
    data = GP_CATCH_DIC[code]
    stock = data['list']
    close = data['lastclose']       # 昨日收盘价
    open = data['open']             # 开盘价
    curprice = float(stock[stock_price])   # 当前价格
    st = data.get('st',False)       # 是否st

    #涨停
    ztprice = float(tools.getzt(close,st))
    if curprice == ztprice:
        if code not in GP_ZT_LIST:
            GP_ZT_LIST.append(code)
            if open == curprice:
                #竞价涨停
                msg = '[竞价][' + stock[stock_time] + '] ' + data['name'] + ' ' + code + ' 竞价涨停 ' + BK_NAME_CATCH_DIC[code]
            else:
                #涨停
                msg = '[涨停][' + stock[stock_time] + '] ' + data['name'] + ' ' + code  + ' 冲击涨停 ' + BK_NAME_CATCH_DIC[code]
            #if id in GP_LB_LIST.keys():
            #    s = s + '（' + str(GP_LB_LIST[id] + 1) + '连板)'
            #else:
            #    s = s + '(首板)'
            #TIP_CATCH_LIST.append(msg)
            sendmsg.add(msg)


    #跌停
    dtprice = float(tools.getdt(close,st))
    if curprice == dtprice:
        if code not in GP_DT_LIST:
            GP_DT_LIST.append(code)
            if open == curprice:
                #竞价跌停
                msg = '[竞价][' + stock[stock_time] + '] ' + data['name'] + ' ' + code  + ' 竞价跌停 ' + BK_NAME_CATCH_DIC[code]
            else:
                #跌停
                msg = '[跌停][' + stock[stock_time] + '] ' + data['name'] + ' ' + code  + ' 冲击跌停 ' + BK_NAME_CATCH_DIC[code]
            #TIP_CATCH_LIST.append(msg)
            sendmsg.add(msg)

    '''
    else:
        #涨停开板
        if id in GP_ZT_LIST:
            if FIRST_INIT != 1:
                if id in GP_ZT_CNT.keys():
                    GP_ZT_CNT[id] = GP_ZT_CNT[id] + 1
                else:
                    GP_ZT_CNT[id] = 1
                s = '[开板][' + _otime + '] ' + _oname + ' ' + id + ' 打开涨停板'
                qq.senMsgToBuddy(s)
                qq.sendMsgToGroup(s)
            GP_ZT_LIST.remove(id)
            GP_CZT_LIST.remove(id)
            return
          
        #跌停开板
        if id in GP_DT_LIST:
            if FIRST_INIT != 1:
                if id in GP_DT_CNT.keys():
                    GP_DT_CNT[id] = GP_DT_CNT[id] + 1
                else:
                    GP_DT_CNT[id] = 1
                s = '[翘板][' + _otime + '] ' + _oname + ' ' + id + ' 打开跌停板'
                qq.senMsgToBuddy(s)
                qq.sendMsgToGroup(s)
            GP_DT_LIST.remove(id)
            GP_CDT_LIST.remove(id)
            return
    #print('  GP_ZT_LIST cnt:' + str(len(GP_ZT_LIST)) + '  GP_DT_LIST cnt:' + str(len(GP_DT_LIST)))
    #print(GP_ZT_LIST)
    '''

#新高
GP_XG_DIC = {}                          # 股票新高记录
HIGPUP_OLD_TIP = {}                     # 新高提示列表
def highup(code):
    global GP_XG_DIC,HIGPUP_OLD_TIP


'''
        global GP_CATCH_DIC, GP_XG_DIC, GP_XG_TIP_DIC
        data = GP_CATCH_DIC[id]
        _o = data.get('list', [])
        _omax = float(_o[4])  # 今日最高价

        # 没有数据
        if id not in GP_XG_DIC.keys():
            return

        xgdata = GP_XG_DIC.get(id, {})
        maxkey = 0
        for key, value in xgdata.items():
            if _omax > value and value != 0:
                maxkey = getmax(maxkey, key)

        maxkey = int(maxkey)
        if maxkey == 0 or maxkey == 10 or maxkey == 20:
            return

        if id not in GP_XG_TIP_DIC:
            GP_XG_TIP_DIC[id] = {}

        maxkey = str(maxkey)
        if maxkey not in GP_XG_TIP_DIC[id]:
            GP_XG_TIP_DIC[id][maxkey] = 1
            if FIRST_INIT != 1:
                s = '[新高][' + _o[31] + '] ' + data['name'] + ' ' + id + ' ' + maxkey + '日新高'
                qq.senMsgToBuddy(s)
                qq.sendMsgToGroup(s)
'''


#平台突破
GP_PT_DIC = {}                  #平台数据
PLATFORMUP_OLD_TIP = []         #突破平台提示 向上
PLATFORMDOWN_OLD_TIP = []       #突破平台提示 向下
def platformup(code):
    global GP_CATCH_DIC,GP_PT_DIC,PLATFORMUP_OLD_TIP,PLATFORMDOWN_OLD_TIP
    data = GP_CATCH_DIC[code]
    stock = data['list']

    '''
    _ocur = float(_o[3])  # 当前价格

    # 停牌
    if _ocur == 0:
        return

    # 没有数据
    if id not in GP_PT_DIC.keys():
        return

    ptdata = GP_PT_DIC.get(id,{})

    # 向上
    if id not in GP_PT_TIP_U_LIST:
        hightip = ptdata['high'] * 1.1
        if _ocur > hightip:
            GP_PT_TIP_U_LIST.append(id)
            if FIRST_INIT != 1:
                s = '[平台][' + _o[31] + '] ' + data['name'] + ' ' + id + ' 向上平台突破'
                qq.senMsgToBuddy(s)
                qq.sendMsgToGroup(s)

    # 向下
    if id not in GP_PT_TIP_D_LIST:
        downtip = ptdata['low'] * 0.9
        if _ocur < downtip:
            GP_PT_TIP_D_LIST.append(id)
            if FIRST_INIT != 1:
                s = '[平台][' + _o[31] + '] ' + data['name'] + ' ' + id + ' 向下平台突破'
                qq.senMsgToBuddy(s)
                qq.sendMsgToGroup(s)
'''
############################################################
##通用全局
GLOBAL_CONN = None                      #mysql链接
############################################################

###############################################################################################
# sina沪深股票
###############################################################################################
GP_ALL_STR_URL_LIST = []                # sina全部股票拼接url
GP_ALL_STR_CNT = 710                    # sina拼接返回最大个数868
GP_URL = 'http://hq.sinajs.cn/list='    # sina财经url

#初始化
def sinainit():
    global GLOBAL_CONN
    if GLOBAL_CONN == None:
        print('[dog] sinainit db err')
        return

    global GP_ALL_STR_URL_LIST,GP_ALL_STR_CNT,GP_URL,BK_CATCH_DIC,BK_NAME_CATCH_DIC#,GP_XG_DIC,GP_PT_DIC,GP_LB_LIST#GP_CUR_DATE
    url = GP_URL
    cnt = 0
    cursor = GLOBAL_CONN.cursor()

    # 版块数据
    cursor.execute("SELECT * FROM bk")
    res = cursor.fetchall()
    bknamelist = {}
    for row in res:
        id = row[0]
        name = row[1]
        bknamelist[id] = name

    # 股票列表数据
    cursor.execute("SELECT * FROM code")
    res = cursor.fetchall()
    for row in res:
        code = row[0]
        #缓存数据build
        GP_CATCH_DIC[code] = {}
        GP_CATCH_DIC[code]['list'] = {}

        #版块数据
        bk = row[9]
        bk = bk.replace('[','')
        bk = bk.replace(']','')
        bkdata = bk.split(',')
        BK_CATCH_DIC[code] = bkdata
        bkname = ''
        for id in bkdata:
            bkname += '[' + bknamelist[int(id)] + ']'
        BK_NAME_CATCH_DIC[code] = bkname

        # sina url拼接
        if int(code) >= 600000:
            symbol = 'sh' + code
        else:
            symbol = 'sz' + code
        url += symbol + ','
        cnt = cnt + 1
        if cnt >= GP_ALL_STR_CNT:
            GP_ALL_STR_URL_LIST.append(url[:-1])
            url = GP_URL
            cnt = 0


'''
    # local xg
    cursor.execute("SELECT * FROM xg")
    res = cursor.fetchall()
    for row in res:
        rlist = {}
        rlist[10] = row[1] / 100
        rlist[20] = row[2] / 100
        rlist[30] = row[3] / 100
        rlist[40] = row[4] / 100
        rlist[50] = row[5] / 100
        rlist[60] = row[6] / 100
        GP_XG_DIC[row[0]] = rlist

    # local pt
    cursor.execute("SELECT * FROM pt")
    res = cursor.fetchall()
    for row in res:
        rlist = {}
        rlist['high'] = row[1] / 100
        rlist['low'] = row[2] / 100
        GP_PT_DIC[row[0]] = rlist

    # local lb
    cursor.execute("SELECT * FROM lb")
    res = cursor.fetchall()
    for row in res:
        GP_LB_LIST[row[0]] = row[1]
    # print(GP_LB_LIST)
    cursor.close()

    # load data for sina
    fr = open('gp.txt', 'r',encoding='UTF-8')
    for line in fr:
        tmp = line.split(',')
        dic = {}
        id = tmp[0]
        url = tmp[1] + id
        #dic['url'] = url
        #dic['name'] = tmp[2].replace('\\n','',1)
        dic['list'] = []
        GP_CATCH_DIC[id] = dic
        dic2 = {}
        dic2['list'] = []
        GP_JJ_CATCH_DIC[id] = dic2
        _URL += url + ','
        cnt = cnt + 1
        if cnt >= GP_ALL_STR_CNT:
            _URL = _URL[:-1]
            GP_ALL_STR_URL_LIST.append(_URL)
            _URL = GP_URL
            cnt = 0

'''


############################################################
##主控函数
def init():
    global GLOBAL_CONN
    #读取mysql连接
    GLOBAL_CONN = pymysql.connect(host='192.168.1.103', user='root', password='Admin123!', db='gp', port=3306, charset='utf8')
    #GLOBAL_CONN = pymysql.connect(host='106.14.152.18', user='stockMarket', password='kdarrkmpjX5kCbTe', db='stockMarket', port=3306, charset='utf8')
    #GLOBAL_CONN = pymysql.connect(host='localhost', user='root', password='admin123!', db='gp', port=3306, charset='utf8')

def destroy():
    global GLOBAL_CONN
    if GLOBAL_CONN != None:
        GLOBAL_CONN.close()
        GLOBAL_CONN = None

def start():
    init()
    sinainit()
    destroy()


def update():
    dog()
    #print('[dog] update')



#start()
#update()