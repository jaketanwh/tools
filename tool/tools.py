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
    
    def getlastday():
    lastdate = datetime.date.today()
    oneday = datetime.timedelta(days = 1)
    str = lastdate.strftime('%Y%m%d')
    ret = -1
    while ret != 0:
        ret,data = net.tushare_trade(str,str)
        if ret != -1:
            if data['is_open'][0] == 1:
                break
            if ret == 0:
                lastdate -= oneday
                str = lastdate.strftime('%Y%m%d')
            ret = -1

    return lastdate
    """

#今日是否交易日 0休市 1交易
def gettodaytrade():
    today = datetime.date.today()
    str = today.strftime('%Y%m%d')
    ret = -1
    #while ret != 0:
    ret,data = net.tushare_trade(str,str)
    return 1#data['is_open'][0]

#取前n个时间差日期
def getnday(n):
    lastdate = getlastday()
    oneday = datetime.timedelta(days=1)
    while n > 0:
        n -= 1
        lastdate -= oneday
    return lastdate

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

#取指定涨幅价
def getpercent(close,percent):
    _corl = percent / 100 + 1
    pj = Decimal(close * _corl).quantize(Decimal('0.00'))
    pj = '{:g}'.format(float(pj))
    return float(pj)