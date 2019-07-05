import sys
sys.path.append('../data')
sys.path.append('../msg')
import net,json,time,re
from decimal import *
import sendmsg


###############################################################################################
#  同花顺问财
 ###############################################################################################
#THS_URL = "http://www.iwencai.com/asyn/search?q=%s&queryType=stock&app=qnas&qid="
THS_URL = 'http://www.iwencai.com/stockpick/load-data?typed=0&preParams=&ts=1&f=1&qs=result_original&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w=%s&queryarea='
def thsdata(condition):
    global THS_URL
    url = THS_URL % (condition)
    print(url)
    res = net.send(url, 1, 1)
    print(res)
    if res != -1:
        jdata = json.loads(res)
        print(jdata)
        if jdata and jdata['data'] and jdata['data']['result'] and jdata['data']['result']['result']:
            return jdata['data']['result']['result']
    return -1

THS_TIP_DIC = []                    # 提示列表
def ths():
    res = thsdata(repr('2019年6月10日的涨停'))
    if res != -1:
        print(res)
#ths()

import wencai as wc
report = wc.get_scrape_report("上市天数大于60天；筹码集中度90小于20%；非停牌；非st；")
print(report)

#print(repr('2019年6月10日的涨停'))