#工具类用于读取数据
import sys
sys.path.append('../tool')
import tools

#index
INDEX_MACD  = 13
INDEX_BOLL  = 14
INDEX_VOL   = 5
INDEX_VOL5  = 7
INDEX_VOL10 = 9
INDEX_VOL20 = 11
INDEX_TURN  = 5
INDEX_LB    = 10
#macd
def macd(conn,code,date=None):
    if date == None:
        date = tools.getlastday()
    cursor = conn.cursor()
    sql = "SELECT * FROM `" + code + "` WHERE day = '" + date + "'"
    o = cursor.execute(sql)
    if o > 0:
        res = cursor.fetchall()
        cursor.close()
        global INDEX_MACD
        return res[0][INDEX_MACD]*0.01
    else:
        cursor.close()
        return None


#boll
def boll(conn,code,date=None):
    if date == None:
        date = tools.getlastday()
    cursor = conn.cursor()
    sql = "SELECT * FROM `" + code + "` WHERE day = '" + date + "'"
    o = cursor.execute(sql)
    if o > 0:
        res = cursor.fetchall()
        cursor.close()
        global INDEX_BOLL
        _boll = res[0][INDEX_BOLL]
        _boll = _boll.strip('[]')
        arr = _boll.split(',')
        arr[0] = float(arr[0])
        arr[1] = float(arr[1])
        arr[2] = float(arr[2])
        return arr
    else:
        cursor.close()
        return None


#vol
def vol(conn,code,param,date=None):
    if date == None:
        date = tools.getlastday()
    cursor = conn.cursor()
    sql = "SELECT * FROM `" + code + "` WHERE day = '" + date + "'"
    o = cursor.execute(sql)
    if o > 0:
        res = cursor.fetchall()
        cursor.close()
        global INDEX_MACD
        index = INDEX_VOL
        if param == 5:
            index = INDEX_VOL5
        elif param == 10:
            index = INDEX_VOL10
        elif param == 20:
            index = INDEX_VOL20

        return res[0][index]
    else:
        cursor.close()
        return None

#turn
def turn(conn,code):
    cursor = conn.cursor()
    sql = "SELECT * FROM code WHERE id = '" + code + "'"
    o = cursor.execute(sql)
    if o > 0:
        res = cursor.fetchall()
        cursor.close()
        global INDEX_TURN
        return res[0][INDEX_TURN] * 0.01
    else:
        cursor.close()
        return None

#bkvol
def bkvol(conn,bkid,param,date=None):
    if date == None:
        date = tools.getlastday()
    cursor = conn.cursor()
    sql = "SELECT * FROM code"
    o = cursor.execute(sql)
    if o > 0:
        res = cursor.fetchall()
        cursor.close()
        bkid = str(bkid)
        list = []
        for row in res:
            code = row[0]
            bk = row[9]
            bk = bk.strip('[]')
            arr = bk.split(',')
            for _row in arr:
                if _row == bkid:
                    list.append(code)
                    break
        rsum = 0
        for code in list:
            rres = vol(conn, code, param, date)
            rsum = rsum + rres

        return round(rsum / len(list),2)
    else:
        cursor.close()
        return None

#bkzd
def bkzd(conn, bkid, date=None):
    if date == None:
        date = tools.getlastday()

    cursor = conn.cursor()
    sql = "SELECT * FROM code"
    o = cursor.execute(sql)
    if o > 0:
        res = cursor.fetchall()
        cursor.close()
        bkid = str(bkid)
        upnum,midnum,downnum = 0,0,0
        for row in res:
            percent = row[2]
            bk = row[9]
            bk = bk.strip('[]')
            arr = bk.split(',')
            for _row in arr:
                if _row == bkid:
                    if percent > 0:
                        upnum = upnum + 1
                    elif percent == 0:
                        midnum = midnum + 1
                    else:
                        downnum = downnum + 1
                    break
        return upnum, midnum, downnum
    else:
        cursor.close()
        return None

#lb
def lb(conn,code):
    cursor = conn.cursor()
    sql = "SELECT * FROM code WHERE id = '" + code + "'"
    o = cursor.execute(sql)
    if o > 0:
        res = cursor.fetchall()
        cursor.close()
        global INDEX_LB
        return res[0][INDEX_LB]
    else:
        cursor.close()
        return None