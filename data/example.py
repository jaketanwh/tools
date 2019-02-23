import util
import pymysql

if __name__ == "__main__":
    conn = pymysql.connect(host='localhost', user='root', password='admin123!', db='gp', port=3306,
                                  charset='utf8')

    #macd
    #res = util.macd(conn,'000001','2018-09-21')
    #if res != None:
    #    print(res)

    #boll
    #res = util.boll(conn,'000001','2018-09-21')
    #if res != None:
    #    print(res)

    #vol
    #res = util.vol(conn, '000001', 5,'2018-09-21')
    #if res != None:
    #    print(res)

    #turn
    #res = util.turn(conn, '000001')
    #if res != None:
    #    print(res)

    #bkvol
    #res = util.bkvol(conn,'1',5,'2018-09-21')
    #if res != None:
    #    print(res)

    #bkzd
    #res1,res2,res3 = util.bkzd(conn, '1','2018-09-21')
    #if res1 != None:
    #    print(str(res1) + '-' + str(res2) + '-' + str(res3))

    #lb
    res = util.lb(conn,'000001')
    if res != None:
        print('lb:' + str(res))


    conn.close()