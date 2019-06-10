# code表数据
import sys
sys.path.append('../tool')
import tools
import net
import kpltools
import t_bk

#更新板块表 13min
GLOBAL_BK = {}
def updateBK(name,id,percent):
    global GLOBAL_BK
    # 没有数据
    if name in GLOBAL_BK.keys():
       return GLOBAL_BK[name][0]
    GLOBAL_BK[name] = [id,percent]


#取开盘啦个股数据
def kpl_gg(code):
    lastday = tools.getlastday()
    param = kpltools.build_kpl_gg(code,lastday)
    res = -1
    while (res == -1 or isinstance(res['pankou'],dict) == False or isinstance(res['pankou']['real'],dict) == False):
        res = net.kpl(param)

    #timeout
    if res == -2:
        return -1

    info = {}
    real = res['pankou']['real']
    info['pb'] = real['dyn_pb_rate']                #市净率
    info['percent'] = real['px_change_rate']        #涨跌幅
    info['turnover'] = real['turnover_ratio']       #换手率
    info['sjlt'] = int(real['sjlt'])                #真实流通市值
    info['nmc'] = real['circulation_value']         #流通市值
    info['mktcap'] = real['market_value']           #总市值
    info['high'] = real['high_px']                  #最高价
    info['low'] = real['low_px']                    #最低价
    info['rvol'] = real['vol_ratio']                #量比

    #所属板块及板块涨幅
    bklist = []
    stockplate = res['stockplate']
    if stockplate == None:
        print('[code] ' + res['pankou']['name'] + ' stockplate is NoneType')
    else:
        for row in stockplate:
            print(row)
            bk_name = row[0]     #板块name
            bk_zd = row[1]       # 涨跌幅
            bk_id = row[8]       # 板块id
            #更新bk表数据
            updateBK(bk_name,bk_id,bk_zd)
            bklist.append(bk_id)

    info['bk'] = str(bklist) #','.join()# str.split(',')
    return info

#更新连板数据
def day_lb_calculate(res,st):
    _ban = 0
    _lastclose = 0
    for _row in res:
        _close = _row[2] / 100
        if _lastclose == 0:
            _lastclose = _close
        else:
            _tmp = getdt(_lastclose, st == 1)
            if _tmp == _close:
                _lastclose = _close
                _ban = _ban + 1
            else:
                break
    if _ban > 0:
        return _ban

    return -1

def getdt(close,st):
    if st:
        _corl = 1.05
    else:
        _corl = 1.1
    _dtj = Decimal(close / _corl).quantize(Decimal('0.00'))
    _dtj = '{:g}'.format(float(_dtj))
    return float(_dtj)

# 遍历个股N天数据
def checkeach(cursor,code,st,ban=0):
    cursor.execute("SELECT high,low,close FROM `" + code + "` p ORDER BY p.day DESC LIMIT 20")
    res = cursor.fetchall()
    if ban == 0:
        _lastclose = 0
        for _row in res:
            _close = _row[2] * 0.01
            if _lastclose == 0:
                _lastclose = _close
            else:
                _tmp = tools.getzt(_lastclose, st == 1)
                if _tmp == _close:
                    _lastclose = _close
                    ban = ban + 1
                else:
                    break
    else:
        ban = 0
    sql = ("UPDATE code SET lb=%d WHERE id = '" + code + "'") % (ban)
    cursor.execute(sql)

# 使用tushare 更新代码，st
def ts_updatecode(conn, today):
    if today.empty:
        return -1

    _list = {}
    _len = str(len(today))
    for i, row in today.iterrows():
        #code = row['ts_code']
        code = row['symbol']

        #if k != '30' and k != '60' and k != '00':
        #    continue

        #if row['trade'] == 0:
        #    continue

        info = -1
        while info == -1:
            info = kpl_gg(code)

        print('[Code] kpl gg update - ' + code + '[' + str(i+1) + '/' + _len + ']')

        if row['name'].find('ST') >= 0:
            st = 1
        else:
            st = 0

        info['st'] = st                                         # st 1.是 0.否
        #info['pb'] = round(info['pb'] * 100)                    # 市净率 保留两位四舍五入
        #info['per'] = round(row['per'] * 100)                   # 市盈率 保留两位四舍五入
        info['percent'] = round(info['percent'] * 100)          # 涨跌幅 保留两位四舍五入
        info['turnover'] = round(info['turnover'] * 100)        # 换手率 保留两位四舍五入
        info['sjlt'] = round((info['sjlt']) * 0.0001)           # 真实流通市值 计数万单位
        info['nmc'] = round((info['nmc']) * 0.0001)             # 流通市值 计数万单位
        info['mktcap'] = round((info['mktcap']) * 0.0001)       # 总市值 计数万单位
        info['high'] = round(info['high'] * 100)                # 最高价 保留两位四舍五入
        info['low'] = round(info['low'] * 100)                  # 最低价 保留两位四舍五入
        info['rvol'] = round(info['rvol'] * 100)                # 量比
        _list[code] = info

    # 游标
    cursor = conn.cursor()
    # 创建code表   代码(id) 是否st(st 1.是 0.不是) 涨跌(percent) 市净率(pb) 市盈率(per) 换手(turnover) 总市值(mktcap) 流通市值(nmc) 真实市值(sjlt) 板块[名字1,名字2...](bk) 连板次数(lb)
    if tools.table_exists(cursor, 'code') == 0:
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS code(id TEXT,st TINYINT(1),percent SMALLINT,pb MEDIUMINT, per MEDIUMINT,turnover SMALLINT UNSIGNED,nmc INT UNSIGNED,mktcap INT UNSIGNED,sjlt INT UNSIGNED,bk TEXT,lb TINYINT UNSIGNED,high INT UNSIGNED,low INT UNSIGNED,rvol INT UNSIGNED)")

    # 写入code表数据
    for key, value in _list.items():
        st = value['st']
        nmc = value['nmc']
        mkcap = value['mktcap']
        pb = 0#value['pb']
        per = 0#value['per']
        sjlt = value['sjlt']
        percent = value['percent']
        turnover = value['turnover']
        high = value['high']
        low = value['low']
        rvol = value['rvol']

        bk = value['bk'].replace('\'', '')

        cursor.execute("SELECT * FROM code WHERE id=%s", key)
        res = cursor.fetchall()
        if len(res) == 0:
            sql = "INSERT INTO code(id,st,percent,pb,per,turnover,nmc,mktcap,sjlt,bk,high,low,rvol) VALUES('%s','%d','%d','%d','%d','%d','%d','%d','%d','%s', '%d', '%d', '%d')" % (key, st, percent, pb, per, turnover, nmc, mkcap, sjlt, bk, high, low, rvol)
            print(sql)
            cursor.execute(sql)
        else:
            sql = ("UPDATE code SET st=%d,percent=%d,pb=%d,per=%d,turnover=%d,nmc=%d,mktcap=%d,sjlt=%d,bk=%s,high=%d,low=%d,rvol=%d WHERE id = '" + key + "'") % (st, percent, pb, per, turnover, nmc, mkcap, sjlt, "'" + bk + "'", high, low, rvol)
            print(sql)
            cursor.execute(sql)

    conn.commit()
    cursor.close()
    return 0

def update(conn):
    global GLOBAL_BK
    GLOBAL_BK = {}
    serverTime,serverDay = tools.get_servertime()
    print('[Code] 开始更新表 ' + "%s/%s/%s " %(serverTime.tm_year,serverTime.tm_mon, serverTime.tm_mday))
    ret = -1
    while ret == -1:
        ret,today = net.tushare_today()

    ret = ts_updatecode(conn,today)
    if ret != 0:
        print('[code]表更新错误')
        return ret

    print('[Code]表更新完成')
    t_bk.update(conn,GLOBAL_BK)
    return ret

def completedupdate(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM code")
    res = cursor.fetchall()
    for row in res:
        code = row[0]
        st = row[1]
        percent = row[2] * 0.01
        if percent > 9.5:
            checkeach(cursor,code,st)
        else:
            checkeach(cursor,code,st,-1)

    conn.commit()
    cursor.close()