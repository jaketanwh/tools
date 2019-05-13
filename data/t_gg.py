#个股表数据
import sys
sys.path.append('../tool')
import net
import tools
import pandas as pd
import talib
import time

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

#boll
def getboll(df):
    #提取收盘价
    closed = df['close'].values
    upper, middle, lower = talib.BBANDS(closed,matype=talib.MA_Type.T3)
    return upper,middle,lower

#sina day
def sina_updategg(conn):
    #params
    SINA_DAY = "60"
    SINA_MA = '5,10,20'
    SINA_SCALE = '240'

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM code")
    res = cursor.fetchall()
    index = 1
    rlen = len(res)
    for row in res:
        # 代码(id) 是否st(st 1.是 0.不是) 涨跌(percent) 市净率(pb) 市盈率(per) 换手(turnover) 总市值(mktcap) 流通市值(nmc) 真实市值(sjlt) 板块[名字1,名字2...](bk)
        code = row[0]
        print('[GG] loading:(' + str(index) + '/' + str(rlen) + ') - ' + code)
        index = index + 1

        #1.sina
        data = -1
        while data == -1:
            data = net.sina_history(code, SINA_SCALE, SINA_MA, SINA_DAY)

        #2.tushare
        df = net.tushare_history(code)
        #macd
        macd = getmacd(df)
        macddata = macd.set_index('date')
        #boll
        upper, middle, lower = getboll(df)

        if tools.table_exists(cursor, code) == 0:
            csql = "CREATE TABLE IF NOT EXISTS `" + code + "`(day date,open mediumint unsigned,high mediumint unsigned,low mediumint unsigned,close mediumint unsigned,volume bigint unsigned,ma_price5 mediumint unsigned,ma_volume5 bigint unsigned,ma_price10 mediumint unsigned,ma_volume10 bigint unsigned,ma_price20 mediumint unsigned,ma_volume20 bigint unsigned,turn mediumint unsigned,macd mediumint,boll text)"
            cursor.execute(csql)

        idx = len(upper) - 1
        for o in data:
            date = o['day']
            ssql = "SELECT * FROM `" + code + "` WHERE day = '" + date + "'"
            has = cursor.execute(ssql)

            map5 = round(o.get('ma_price5', 0) * 100)
            mav5 = int(o.get('ma_volume5', 0))
            map10 = round(o.get('ma_price10', 0) * 100)
            mav10 = int(o.get('ma_volume10', 0))
            map20 = round(o.get('ma_price20', 0) * 100)
            mav20 = int(o.get('ma_volume20', 0))
            macdval = round(macddata.ix[str(date), 'data_macd']*100)
            boll = str([round(upper[idx],2),round(middle[idx],2),round(lower[idx],2)])

            if has == 0:
                s = "INSERT INTO `" + code + "`(day,open,high,low,close,volume,ma_price5,ma_volume5,ma_price10,ma_volume10,ma_price20,ma_volume20,macd,boll) VALUES('%s','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%s')"
                sql = s % (
                    o['day'], int(float(o['open']) * 100), int(float(o['high']) * 100), int(float(o['low']) * 100),
                    int(float(o['close']) * 100), int(o['volume']), map5,mav5,map10,mav10,map20,mav20,macdval,boll)
            else:
                s = "UPDATE `" + code + "` SET open=%d,high=%d,low=%d,close=%d,volume=%d,ma_price5=%d,ma_volume5=%d,ma_price10=%d,ma_volume10=%d,ma_price20=%d,ma_volume20=%d,macd=%d,boll=%s WHERE day = '" + o['day'] + "'"
                sql = s % (int(float(o['open']) * 100), int(float(o['high']) * 100), int(float(o['low']) * 100),
                           int(float(o['close']) * 100), int(o['volume']), map5,mav5,map10,mav10,map20,mav20,macdval,"'"+boll+"'")
            if idx > 0:
                idx = idx - 1
            cursor.execute(sql)
        conn.commit()
    cursor.close()
    return 0


def tushare_updategg(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM code")
    res = cursor.fetchall()
    index = 1
    rlen = len(res)
    currtime = tools.getlastday().strftime("%Y%m%d")
    starttime = tools.getnday(60).strftime("%Y%m%d")
    fields = "turnover_rate,turnover_rate_f,volume_ratio,pe,pb"
    for row in res:
        # 代码(id) 是否st(st 1.是 0.不是) 涨跌(percent) 市净率(pb) 市盈率(per) 换手(turnover) 总市值(mktcap) 流通市值(nmc) 真实市值(sjlt) 板块[名字1,名字2...](bk)
        code = row[0]
        print('[GG] loading:(' + str(index) + '/' + str(rlen) + ') - ' + code)
        index = index + 1

        #1.tushare
        ret = -1
        while ret == -1:
            ret,df = net.tushare_history(code, starttime, currtime)

        list = {}
        for _i, _row in df.iterrows():
            info = {}
            date = _row['trade_date']
            info['open'] = _row['open']             #开盘价
            info['high'] = _row['high']             #最高价
            info['low'] = _row['low']               #最低价
            info['close'] = _row['close']           #收盘价
            info['pre_close'] = _row['pre_close']   #昨收价
            #change = _row['change']                #涨跌额
            #info['pct_chg'] = _row['pct_chg']       #涨跌幅
            info['volume'] = _row['vol']               #成交量（手）
            info['amount'] = _row['amount']         #成交额（千元）
            ret = -1
            while ret == -1:
                ret,fdf = net.tushare_history_fields(code, date, fields)
            for __i, __row in fdf.iterrows():
                info['turn'] = __row['turnover_rate']            #换手率
                info['turnover'] = __row['turnover_rate_f']      #换手率（自由流通股）
                info['volume_ratio'] = __row['volume_ratio']     #量比
                info['pe'] = __row['pe']                         #市盈率（总市值/净利润）
                info['pb'] = __row['pb']                         #市净率（总市值/净资产）
            list[date] = info

        #macd
        #macd = getmacd(df)
        #macddata = macd.set_index('date')
        #boll
        #upper, middle, lower = getboll(df)

        if tools.table_exists(cursor, code) == 0:
            csql = "CREATE TABLE IF NOT EXISTS `" + code + "`(day date,open mediumint unsigned,high mediumint unsigned,low mediumint unsigned,close mediumint unsigned,volume bigint unsigned,amount bigint unsigned,turn mediumint unsigned,turnover mediumint unsigned,vol mediumint unsigned,pe mediumint unsigned,pb mediumint unsigned,preclose mediumint unsigned)"
            cursor.execute(csql)

        #idx = len(upper) - 1
        for key, value in list.items():
            date = key
            open = value['open']                            #开盘价
            high = value['high']                            #最高价
            low = value['low']                              #最低价
            close = value['close']                          #收盘价
            pre_close = value['pre_close']                  #昨收价
            #pct_chg = value['pct_chg']                      #涨跌幅
            volume = value['volume']                        #成交量（手）
            amount = value['amount']                        #成交额（千元）
            turn = value['turn']                            #换手率
            turnover = value['turnover']                    #换手率（自由流通股）
            vol = value['volume_ratio']                     #量比
            pe = value['pe']                                #市盈率（总市值/净利润）
            pb = value['pb']                                #市净率（总市值/净资产）

            if open is None:
                open = 0
            if high is None:
                high = 0
            if low is None:
                low = 0
            if close is None:
                close = 0
            if pre_close is None:
                pre_close = 0
            if volume is None:
                volume = 0
            if open is None:
                open = 0
            if amount is None:
                amount = 0
            if turn is None:
                turn = 0
            if turnover is None:
                turnover = 0
            if vol is None:
                vol = 0
            if pe is None:
                pe = 0
            if pb is None:
                pb = 0

            print(value)
            ssql = "SELECT * FROM `" + code + "` WHERE day = '" + date + "'"
            has = cursor.execute(ssql)
            if has == 0:
                s = "INSERT INTO `" + code + "`(day,open,high,low,close,volume,amount,turn,turnover,vol,pe,pb,preclose) VALUES('%s','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d')"
                sql = s % (
                    date, int(open * 100), int(high * 100), int(low * 100),
                    int(close * 100), int(volume), int(amount),int(turn * 100),int(turnover * 100),int(vol * 100),int(pe * 100),int(pb*100),int(pre_close*100))
            else:
                s = "UPDATE `" + code + "` SET open=%d,high=%d,low=%d,close=%d,volume=%d,amount=%d,turn=%d,turnover=%d,vol=%d,pe=%d,pb=%d,preclose=%d WHERE day = '" + date + "'"
                sql = s % (int(open * 100), int(high * 100), int(low * 100),
                           int(close * 100), int(volume), int(amount), int(turn * 100), int(turnover * 100),
                           int(vol * 100), int(pe * 100), int(pb * 100), int(pre_close * 100))
            cursor.execute(sql)
        conn.commit()
    cursor.close()
    return 0

def update(conn):
    #ret = sina_updategg(conn)
    ret = tushare_updategg(conn)
    return ret





