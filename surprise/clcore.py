


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

#处理包含并返回缠论K线数据
def initkx(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM code")
    res = cursor.fetchall()
    for row in res:
        # 代码(id) 是否st(st 1.是 0.不是) 涨跌(percent) 市净率(pb) 市盈率(per) 换手(turnover) 总市值(mktcap) 流通市值(nmc) 真实市值(sjlt) 板块[名字1,名字2...](bk)
        _code = row[0]
        cursor.execute("SELECT day,open,high,low,close FROM `" + _code + "` p ORDER BY p.day DESC LIMIT 100")
        _res = cursor.fetchall()
        for _row in _res:
            #_code = _row[0]
            st = _row[1]
            percent = _row[2] * 0.01

    cursor.close()
    return 0
