import sys
sys.path.append('../data')
sys.path.append('../msg')
import net,json,time
from decimal import *
import sendmsg

###############################################################################################
#  同花顺问财
 ###############################################################################################
THS_URL = "http://www.iwencai.com/asyn/search?q=%s&queryType=stock&app=qnas&qid="
def thsdata(condition):
    global THS_URL
    url = THS_URL % (condition)
    print(url)
    res = net.send(url, 1, 1)
    if res != -1:
        jdata = json.loads(res)
        print(jdata)
        if jdata and jdata['data'] and jdata['data']['result'] and jdata['data']['result']['result']:
            return jdata['data']['result']['result']
    return -1

THS_TIP_DIC = []                    # 提示列表
def ths():
    res = thsdata('2019年6月10日的涨停')
    if res != -1:
        print(res)
