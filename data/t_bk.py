# bk表数据
import sys
sys.path.append('../tool')
import tools
import kpltools

#开盘啦板块详情
def kpl_bk(code):
    param = kpltools.build_kpl_bk(code)
    

def update(conn,t_bk):
    print('[BK] 表开始更新')
    # 写入游标
    cursor = conn.cursor()

    # 创建bk表 板块id(id) 名字(name) 涨跌(percent)
    if tools.table_exists(cursor, 'bk') == 1:
        cursor.execute("DROP TABLE bk")
    cursor.execute("CREATE TABLE IF NOT EXISTS bk(id MEDIUMINT UNSIGNED,name TEXT,percent SMALLINT)")


    for name,row in t_bk.items():
        id      = int(row[0])               #板块id
        percent = round(row[1] * 100)       #涨跌幅 保留两位四舍五入
        cursor.execute("INSERT INTO bk(id,name,percent) VALUES('%d','%s','%d')" % (id, name, percent))

    conn.commit()
    cursor.close()
    print('[BK] 表更新完成')
