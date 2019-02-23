import pymysql
import clcore

#格式化缠论K线
def formatCLK():
    global GLOBAL_CONN
    clcore.initkx(GLOBAL_CONN)



############################################################
##主控函数
def init():
    global GLOBAL_CONN
    #读取mysql连接
    GLOBAL_CONN = pymysql.connect(host='192.168.1.103', user='root', password='Admin123!', db='lanjingling', port=3306, charset='utf8')

def destroy():
    global GLOBAL_CONN
    GLOBAL_CONN.close()
    GLOBAL_CONN = None

def start():
    init()
    formatCLK()
    destroy()