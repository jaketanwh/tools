
import time

#开盘啦个股数据
def build_kpl_gg(code,day = time.strftime("%Y%m%d", time.localtime())):
    param = {}
    param['a'] = 'GetHQPlate'
    param['c'] = 'PCArrangeData'
    param['Day'] = day
    param['StockID'] = code
    param['SelType'] = '3,8,7'        #1.trend 2.chouma 3.pankou 8.stockplate 7.selval
    return param

#开盘啦板块数据
def build_kpl_bk(code):
    param = {}
    param['a'] = 'GetPlateKLineDay'
    param['c'] = 'ZhiShuKLine'
    param['st'] = 160
    param['Type'] = 'd'
    param['StockID'] = code
    return param