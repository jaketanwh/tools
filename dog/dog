import pymysql


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
    global GLOBAL_CONN,GP_ALL_STR_URL_LIST,GP_ALL_STR_CNT,GP_URL#,GP_XG_DIC,GP_PT_DIC,GP_LB_LIST#GP_CUR_DATE
    #_URL = GP_URL
    #cnt = 0

    if GLOBAL_CONN == None:
        print('[dog] sinainit db err')
        return

    cursor = GLOBAL_CONN.cursor()
    cursor.execute("SELECT * FROM code")
    res = cursor.fetchall()
    for row in res:
        print(row)

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

    if cnt > 0:
        _URL = _URL[:-1]
        GP_ALL_STR_URL_LIST.append(_URL)
'''


############################################################
##主控函数
def init():
    global GLOBAL_CONN
    #读取mysql连接
    #GLOBAL_CONN = pymysql.connect(host='192.168.1.103', user='root', password='Admin123!', db='gp', port=3306, charset='utf8')
    #GLOBAL_CONN = pymysql.connect(host='106.14.152.18', user='stockMarket', password='kdarrkmpjX5kCbTe', db='stockMarket', port=3306, charset='utf8')
    GLOBAL_CONN = pymysql.connect(host='localhost', user='root', password='admin123!', db='gp', port=3306, charset='utf8')
    #GLOBAL_CONN = pymysql.connect(host='192.168.1.103', user='root', password='Admin123!', db='lanjingling', port=3306, charset='utf8')

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
   print('[dog] update')



start()