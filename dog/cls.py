import sys
sys.path.append('../data')
sys.path.append('../msg')
import net,json,re,time
import sendmsg

###############################################################################################
# 财联社
CLS_CATCH_LIST = []  # 财联社缓存列表
CLS_URL = 'https://www.cailianpress.com/'
###############################################################################################

def update():
    global CLS_URL
    res = net.send(CLS_URL, 0)
    if res != -1:
        global CLS_CATCH_LIST

        baseinfo = re.findall(".*__NEXT_DATA__ = (.*)\\n          module=.*", res)
        if len(baseinfo) <= 0:
            return

        data = json.loads(baseinfo[0])
        dataList = data['props']['initialState']['telegraph']['dataList']
        for info in dataList:
            level = info['level']
            if level == 'B' or level == 'A':
                id = info['id']
                if id not in CLS_CATCH_LIST:
                    CLS_CATCH_LIST.append(id)
                    ctime = info['ctime']
                    content = info['content']
                    pat = re.compile(r'<[^>]+>', re.S)
                    content = pat.sub('', content)
                    # modified_time = info['modified_time']
                    ftime = time.strftime("%H:%M:%S", time.localtime(ctime))
                    msg = '[财联社]' + '[' + ftime + ']' + content
                    print(msg)
                    sendmsg.add(msg)

        if len(CLS_CATCH_LIST) > 30:
            CLS_CATCH_LIST.pop()