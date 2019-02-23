
import requests
import tushare
import json

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
        if typ == 1:
            html_doc = str(code_of_html.content, 'utf-8')
            return html_doc
        else:
            return code_of_html.text
    else:
        print('[html] error:',code_of_html.status_code)
        return -1


#send post
def sendpost(url,param):
    try:
        headers = defaultheaders()
        code_of_html = requests.post(url, data=param, headers=headers)
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
#今日行情
def tushare_today():
    try:
        today = tushare.get_today_all()
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
def tushare_history(code,start='',end='',ktype='D',autype='qfq',index=False,retry_count=3,ause=0.001):
    df = tushare.get_k_data(code,start,end,ktype,autype,index,retry_count,ause)
    return df

#个股

######################################################################################
# 开盘啦
######################################################################################
KPL_RUL = 'https://pchq.kaipanla.com/w1/api/index.php'
KPL_TOKEN = '5905a7ec37fa0f49a74b8bcef802cea7'
KPL_USERID = 'UserID'
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