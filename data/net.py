
import requests
import tushare
import json
import time


'''
head
'''
def allheaders():
    headers = {
        'Host':'www.iwencai.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
        'Accept':'application/json, text/javascript, */*; q=0.01',
        'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zAj0cAEQKOmPYSZ4PWGXP0lNnT5g22nHvewjVAP-CeRTDNlPK'
                          'h-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding':'gzip,deflate',
        'Referer': 'http://www.iwencai.com/stockpick/search?typed=0&preParams=&ts=1&f=1&qs=result_original&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w=2018%2F7%2F5%20%E5%B9%B4%E7%BA%BF%E4%B8%8A&queryarea=',
        'hexin-v': 'Ap--avq0OGnEhzx1GeQN6OVxLfIoBPOfDVn3mjHsOR-VkbHgOdSD9h0oh-xC',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': 'cid=d39902441188593815b9de4a660beafe1512962748; ComputerID=d39902441188593815b9de4a660beafe1512962748; v=Ap--avq0OGnEhzx1GeQN6OVxLfIoBPOfDVn3mjHsOR-VkbHgOdSD9h0oh-xC; guideState=1; PHPSESSID=b9b44bc6f0b2832d1c1d80f334837c15',
        'Connection': 'keep-alive'
    }
    return headers

def defaultheaders():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1;Win64;x64;rv:61.0)Gecko/20100101 Firefox/61.0"
    }
    return headers


#send get
def send(url,typ=0,default=0):
    if default == 1:
        headers = allheaders()
    else:
        headers = defaultheaders()

    try:
        code_of_html = requests.get(url,headers=headers)
    except Exception as ee:
        print("[net] error")
        return -1

    if code_of_html.status_code == 200:
        '''
        if typ == 1:
            print('code_of_html text')
            print(code_of_html.text)
            html_doc = str(code_of_html.content, 'utf-8')
            return html_doc
        else:
        '''
        return code_of_html.text
    else:
        print('[html] error:',code_of_html.status_code)
        return -1


#send post
def sendpost(url,param):
    try:
        headers = defaultheaders()
        code_of_html = requests.post(url, data=param, headers=headers, timeout=5)
        if code_of_html.status_code != 200:
            return -1
    except requests.exceptions.Timeout:
        print("[net] timeout")
        return -2
    except Exception as ee:
        print("[net] error")
        return -1

    return code_of_html.text



######################################################################################
# tushare
######################################################################################
TUSHARE_INIT = 0    #0.未初始化 1.初始化
TUSHARE_TOKEN = '55d930af86ad6b90068ff8e51c31aa35324d3a11329485ffbc7944ae'
def tushare_init():
    global TUSHARE_INIT, TUSHARE_TOKEN
    if TUSHARE_INIT == 0:
        tushare.set_token(TUSHARE_TOKEN)
        TUSHARE_INIT = 1
    return tushare.pro_api()

#查询当前所有正常上市交易的股票列表
def tushare_today():
    try:
        pro = tushare_init()
        today = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')

        #today = tushare.get_today_all()
    except Exception as ee:
        print("[tushare] today faild")
        return -1,-1
    return 0,today

#个股历史数据
"""
get_k_data(code=None, start='', end='',ktype='D',autype='qfq',index=False,retry_count=3,ause=0.001):
    获取k线数据
    ---------
    Parameters:
      code:string   股票代码 e.g. 600848
      start:string  开始日期 format：YYYY-MM-DD 为空时取当前日期
      end:string    结束日期 format：YYYY-MM-DD 为空时取去年今日
      autype:string 复权类型，qfq-前复权 hfq-后复权 None-不复权，默认为qfq
      ktype：string  数据类型，D=日k线 W=周 M=月 5=5分钟 15=15分钟 30=30分钟 60=60分钟，默认为D
      retry_count : int, 默认 3  如遇网络等问题重复执行的次数
      ause : int, 默认 0 重复请求数据过程中暂停的秒数，防止请求间隔时间太短出现的问题
      drop_factor : bool, 默认 True   是否移除复权因子，在分析过程中可能复权因子意义不大，但是如需要先储存到数据库之后再分析的话，有该项目会更加灵活
"""
#def tushare_history(code,start='',end='',ktype='D',autype='qfq',index=False,retry_count=3,ause=0.001):
#    df = tushare.get_k_data(code,start,end,ktype,autype,index,retry_count,ause)
#    return df
"""
日线行情
ts_code 	str 	股票代码
trade_date 	str 	交易日期
open 	float 	开盘价
high 	float 	最高价
low 	float 	最低价
close 	float 	收盘价
pre_close 	float 	昨收价
change 	float 	涨跌额
pct_chg 	float 	涨跌幅 （未复权，如果是复权请用 通用行情接口 ）
vol 	float 	成交量 （手）
amount 	float 	成交额 （千元）

#ts_code='000001.SZ', start_date='20180701', end_date='20180718'
"""
def tushare_history(code,start,end):
    try:
        pro = tushare_init()
        if int(code) >= 600000:
            symbol = code + '.SH'
        else:
            symbol = code + '.SZ'
        history = pro.daily(ts_code=symbol, start_date=start, end_date=end)
    except Exception as ee:
        print("[tushare] tushare_history faild")
        return -1,-1
    return 0,history

def tushare_old_history(code,typ,start,end):
    try:
        history = tushare.get_hist_data(code, ktype=typ, start=start,end=end)
    except Exception as ee:
        print("[tushare] tushare_history faild")
        return -1,-1
    return 0,history

"""
ts_code 	str 	TS股票代码
trade_date 	str 	交易日期
close 	float 	当日收盘价
turnover_rate 	float 	换手率（%）
turnover_rate_f 	float 	换手率（自由流通股）
volume_ratio 	float 	量比
pe 	float 	市盈率（总市值/净利润）
pe_ttm 	float 	市盈率（TTM）
pb 	float 	市净率（总市值/净资产）
ps 	float 	市销率
ps_ttm 	float 	市销率（TTM）
total_share 	float 	总股本 （万股）
float_share 	float 	流通股本 （万股）
free_share 	float 	自由流通股本 （万）
total_mv 	float 	总市值 （万元）
circ_mv 	float 	流通市值（万元）

#'ts_code,trade_date,turnover_rate,volume_ratio,pe,pb'
"""
def tushare_history_fields(code,start,fields):
    try:
        pro = tushare_init()
        if int(code) >= 600000:
            symbol = code + '.SH'
        else:
            symbol = code + '.SZ'
        history = pro.daily_basic(ts_code=symbol, trade_date=start, fields=fields)
    except Exception as ee:
        print("[tushare] tushare_history_fields faild " + code)
        return -1, -1
    return 0, history



#个股
def tusharepro_common():
    global TUSHARE_TOKEN
    tushare.set_token(TUSHARE_TOKEN)
    pro = tushare.pro_api()
    data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    print(data)
    #df = tushare.pro_bar(ts_code='000001.SZ', adj='qfq', start_date='20190501', end_date='20190505')
    #print(df)


#是否交易日
def tushare_trade(sdate,edate):
    try:
        pro = tushare_init()
        res = pro.trade_cal(exchange='SSE', start_date=sdate, end_date=edate)
    except Exception as ee:
        print("[tushare] tushare_trade faild")
        return -1,-1
    return 0,res

######################################################################################
# 开盘啦
######################################################################################
KPL_RUL = 'https://pchq.kaipanla.com/w1/api/index.php'
KPL_TOKEN = '2efa906af1b5641270b21845a4bea7c0'
KPL_USERID = '228432'
#开盘啦个股数据
def kpl(param):
    global KPL_RUL,KPL_TOKEN,KPL_USERID
    param['Token']  = KPL_TOKEN
    param['UserID'] = KPL_USERID
    res = sendpost(KPL_RUL,param)
    if res == -1:
        print('[kpl] sendpost error')
        return res
    try:
        data = json.loads(res)
    except Exception as ee:
        print("[kpl] json.loads error")
        return -1
    return data



######################################################################################
# sina
######################################################################################
SINA_HISTORY_URL = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=%s&scale=%s&ma=%s&datalen=%s"
#code 代码
#scale 分钟间隔（5、15、30、60、240）
#ma 日均值（5、10、15、20、25）
#len 个数
def sina_history(code,scale,ma,len):
    time.sleep(0.3)
    global SINA_HISTORY_URL
    if int(code) >= 600000:
        symbol = 'sh' + code
    else:
        symbol = 'sz' + code
    url = SINA_HISTORY_URL%(symbol,scale,ma,len)
    res = send(url)
    if res != -1:
        res = res.replace('day', '"day"')
        res = res.replace('open', '"open"')
        res = res.replace('low', '"low"')
        res = res.replace('high', '"high"')
        res = res.replace('close', '"close"')
        res = res.replace('volume:', '"volume":')
        res = res.replace('ma_price5', '"ma_price5"')
        res = res.replace('ma_volume5', '"ma_volume5"')
        res = res.replace('ma_price10', '"ma_price10"')
        res = res.replace('ma_volume10', '"ma_volume10"')
        res = res.replace('ma_price20', '"ma_price20"')
        res = res.replace('ma_volume20', '"ma_volume20"')
        try:
            evalRes = eval(res)
        except Exception as ee:
            print("[sina] eval res faild")
            return -1
        return evalRes
    return -1

if __name__ == "__main__":
    tusharepro_common()
