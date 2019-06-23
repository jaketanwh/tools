import pymysql,sys,datetime,talib
sys.path.append('../tool')
sys.path.append('../data')
import tools,net
import pandas as pd

#macd
def getmacd(df,short=0,long=0,mid=0):
    if short == 0:
        short = 12
    if long == 0:
        long = 26
    if mid == 0:
        mid = 9

    #df = df.drop('code', axis=1)
    # 计算短期的ema，使用pandas的ewm得到指数加权的方法，mean方法指定数据用于平均
    df['sema'] = pd.Series(df['close']).ewm(span=short).mean()
    # 计算长期的ema，方式同上
    df['lema'] = pd.Series(df['close']).ewm(span=long).mean()
    # 填充为na的数据
    df.fillna(0, inplace=True)
    # 计算dif，加入新列data_dif
    df['data_dif'] = df['sema'] - df['lema']
    # 计算dea
    df['data_dea'] = pd.Series(df['data_dif']).ewm(span=mid).mean()
    # 计算macd
    df['data_macd'] = 2 * (df['data_dif'] - df['data_dea'])
    # 填充为na的数据
    df.fillna(0, inplace=True)
    # 返回data的三个新列
    return df[['date', 'data_dif', 'data_dea', 'data_macd']]

# 尾盘选股策略
def xgcl1(stock, data, daytime):#todayhal, cor
    #新股未满30天
    if len(data) < 30:
        return False

    todaydata = data[0]
    if todaydata[0] < daytime:
        print('停盘还是数据不是最新 -' + str(stock))
        #return False

    print(todaydata)
    # 今日一字板
    if todaydata[1] == todaydata[3] and todaydata[1] == todaydata[4]:
        return False

    #1）
    last1week_vol, last2week_vol, last3week_vol = 0, 0, 0
    #2)
    last2day_vol, last1day_vol = 0,0
    #3)
    last2day_close,last1day_close = 0,0
    #4)
    last1day_high, last2day_high, last3day_high = 0,0,0
    #5)
    last1day_low, last2day_low, last3day_low = 0,0,0
    #7)
    today_close = 0
    #8)
    today_vol = 0
    #10)
    today_low = 0
    index = 0
    for o in data:
        #day = o[0]
        #open = o[1]
        close = o[2]
        high = o[3]
        low = o[4]
        volume = o[5]

        #1)
        if index >= 5 and index <= 9:
            last1week_vol += volume
        elif index >= 10 and index <= 14:
            last2week_vol += volume
        elif index >= 15 and index <= 19:
            last3week_vol += volume
        #2)
        if index == 0:
            today_close = close
            today_vol = volume
            today_low = low
        elif index == 1:
            last1day_vol = volume
            last1day_close = close
            last1day_high = high
            last1day_low = low
        elif index == 2:
            last2day_vol = volume
            last2day_close = close
            last2day_high = high
            last2day_low = low
        elif index == 3:
            last3day_high = high
            last3day_low = low

        index = index + 1


    # 1)（上周量能 / 上上周量能）> 1.5 或  上周成交量 > 上上周成交量 >上上上周成交量
    conf_1 = 1.5
    if last1week_vol <= 0 or last2week_vol <= 0:
        return False
    if ((last1week_vol / last2week_vol) < conf_1):
        return False
    if (last1week_vol < last2week_vol) or (last2week_vol < last3week_vol):
        return False

    # 2) 昨日量能是前日的1.5-4倍
    conf_2_1, conf_2_2 = 1.5, 4
    if last1day_vol <= 0 or last2day_vol <= 0:
        return False
    tmp = (last1day_vol / last2day_vol)
    if (tmp < conf_2_1 or tmp > conf_2_2):
        return False
    print('2')
    # 3) 昨日收盘价大于前日收盘价
    if last1day_close <= 0 or last2day_close <= 0:
        return False
    if (last1day_close < last2day_close):
        return False
    print('3')
    # 4) 昨日最高价大于前2日最高价
    if (last1day_high < last2day_high) or (last1day_high < last3day_high):
        return False
    print('4')
    # 5)
    # N-3日最低价低于N-2 日最高价
    if last3day_low >= last2day_high:
        # print('[未满足] N-3日最低价低于N-2 日最高价 - ' + security)
        return False
    # N-3日最低价高于N-2日最低价
    if last3day_low <= last2day_low:
        # print('[未满足] N-3日最低价高于N-2日最低价 - ' + security)
        return False
    # N-1日最低价高于N-2日最低价
    if last1day_low <= last2day_low:
        # print('[未满足] N-1日最低价高于N-2日最低价 - ' + security)
        return False
    # N-1 日收盘价高于N-3日最高价
    if last1day_close <= last3day_high:
        # print('[未满足] N-1 日收盘价高于N-3日最高价 - ' + security)
        return False
    print('5')
    # 6）N-1日上涨幅度大于5%
    conf_9 = 1.05
    if last1day_close <= 0 or last2day_close <= 0:
        return False
    if ((last1day_close / last2day_close) <= conf_9):
        return False
    print('6')
    # 7)当前已涨停
    if last1day_close <= 0 or today_close <= 0:
        return False
    if (today_close / last1day_close) >= 1.1:
        # print('当前已涨停 2 today_close:' + str(today_close) + '   last1day_close:'+str(last1day_close))
        return False
    print('7')
    # 8) 今日的成交量是昨日的0.8倍以下
    conf_5 = 0.8
    if today_vol <= 0 or last1day_vol <= 0:
        return False
    if (today_vol / last1day_vol) > conf_5:
        return False
    print('8')
    # 9) 5F,15F，日线，MACD diff值在0之上
    df = net.tushare_old_history(stock,'D',str(data[-1][0]),str(daytime))
    #macd = getmacd(df)
    #print('macd')
    #print(macd)

    #macd5m = get_macd([security], check_date=todayhal, unit='5m')
    #macd15m = get_macd([security], check_date=todayhal, unit='15m')
    #macd1d = get_macd([security], check_date=todayhal, unit='1d')
    #if macd5m == None or macd15m == None or macd1d == None:
    #    return False
    #if (macd5m[security][0] < 0) or (macd15m[security][0] < 0) or (macd1d[security][0] < 0):
    #    return False

    # 10) 今日(N日)最低价 大于N-2,N-3的最高价
    if ((today_low < last2day_high) or (today_low < last3day_high)):
        return False

    return True

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



def xuangu():
    conn = pymysql.connect(host='192.168.1.103', user='root', password='Admin123!', db='gp', port=3306, charset='utf8')
    #conn = pymysql.connect(host='localhost', user='root', password='admin123!', db='gp', port=3306, charset='utf8')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM code")
    res = cursor.fetchall()
    stocks = {}
    for row in res:
        code = row[0]
        stocks[code] = {}

    daytime = tools.getlastday()
    results = []
    for stock in stocks:
        cursor.execute("SELECT day,open,close,high,low,volume FROM `" + stock + "` p ORDER BY p.day DESC LIMIT 30")
        data = cursor.fetchall()
        ret = xgcl1(stock, data, daytime)
        if ret:
            results.append(stock)

    print('结果:')
    print(results)
    conn.close()
    conn = None
    '''
    stocks = list(get_all_securities(['stock']).index)
    stocks = filter_st(stocks)
    data = get_price(security, end_date=today, count=30,
                     fields=['open', 'close', 'paused', 'high', 'low', 'volume'], frequency='1d')
    
    '''
xuangu()
