#工具类
import re
import http.client
import time,datetime
import json
import net
from decimal import *

#表是否存在
def table_exists(cursor,table_name):
    sql = "show tables;"
    cursor.execute(sql)
    tables = [cursor.fetchall()]
    table_list = re.findall('(\'.*?\')',str(tables))
    table_list = [re.sub("'",'',each) for each in table_list]
    if table_name in table_list:
        return True         #存在
    else:
        return False        #不存在


#北京时间
def get_servertime():
    try:
        conn = http.client.HTTPConnection('www.baidu.com')
        conn.request("GET", "/")
        r = conn.getresponse()
        ts = r.getheader('date')  # 获取http头date部分
        # 将GMT时间转换成北京时间
        ltime = time.strptime(ts[5:25], "%d %b %Y %H:%M:%S")
        ttime = time.localtime(time.mktime(ltime) + 8 * 60 * 60)
        whatday = datetime.datetime(ttime.tm_year, ttime.tm_mon, ttime.tm_mday).strftime("%w")
    except Exception as ee:
        print("get_servertime error")
        return -1,-1
    return ttime,whatday

#取最近一个开盘日
def getlastday():
    lastdate = datetime.date.today()
    oneday = datetime.timedelta(days = 1)
    while lastdate.weekday() > 4:
        lastdate -= oneday
    return lastdate
    """
    lastdate = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    while True:
        day = lastdate.strftime('%Y%m%d')
        url = "http://www.easybots.cn/api/holiday.php?d=" + day
        resp = net.send(url)
        if resp != -1:
            data = json.loads(resp)
            print(data)
            #工作日对应结果为 0, 休息日对应结果为 1, 节假日对应的结果为 2
            if data[str(day)] == "0":
                break
            lastdate -= oneday
    return lastdate
    """

#取涨停价
def getzt(close,st):
    if st:
        _corl = 1.05
    else:
        _corl = 1.1
    ztj = Decimal(close * _corl).quantize(Decimal('0.00'))
    ztj = '{:g}'.format(float(ztj))
    return float(ztj)

#取跌停价
def getdt(close,st):
    if st:
        _corl = 1.05
    else:
        _corl = 1.1
    dtj = Decimal(close / _corl).quantize(Decimal('0.00'))
    dtj = '{:g}'.format(float(dtj))
    return float(dtj)