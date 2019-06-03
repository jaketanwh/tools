import pymysql

#以下是数据表
import t_code,t_gg

############################################################
##通用全局
GLOBAL_CONN = None                      #mysql链接
############################################################

############################################################
#更新code表
def updateCode():
    global GLOBAL_CONN
    if GLOBAL_CONN == None:
        print('[data] updateCode GLOBAL_CONN None')
        return -1
    res = -1
    while res == -1:
        res = t_code.update(GLOBAL_CONN)

#更新个股表
def updateGG():
    global GLOBAL_CONN
    if GLOBAL_CONN == None:
        print('[data] updateGG GLOBAL_CONN None')
        return -1
    res = -1
    while res == -1:
        res = t_gg.update(GLOBAL_CONN)


#数据更新完后统计
def onCompleted():
    global GLOBAL_CONN
    t_code.completedupdate(GLOBAL_CONN)

############################################################
##主控函数
def init():
    global GLOBAL_CONN
    #读取mysql连接
    GLOBAL_CONN = pymysql.connect(host='192.168.1.103', user='root', password='Admin123!', db='gp', port=3306, charset='utf8')
    #GLOBAL_CONN = pymysql.connect(host='106.14.152.18', user='stockMarket', password='kdarrkmpjX5kCbTe', db='stockMarket', port=3306, charset='utf8')
    #GLOBAL_CONN = pymysql.connect(host='localhost', user='root', password='admin123!', db='gp', port=3306, charset='utf8')
    #GLOBAL_CONN = pymysql.connect(host='192.168.1.103', user='root', password='Admin123!', db='lanjingling', port=3306, charset='utf8')

def destroy():
    global GLOBAL_CONN
    if GLOBAL_CONN != None:
        GLOBAL_CONN.close()
        GLOBAL_CONN = None

def start():
    init()
    updateCode()
    updateGG()
    onCompleted()
    destroy()
