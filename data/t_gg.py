#个股表数据
import sys
sys.path.append('../tool')
import net
import tools
import pandas as pd
import talib

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


def update(conn):
    ret = sina_updategg(conn)
    return ret





