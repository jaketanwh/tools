import time,requests,logging,urllib,hashlib,datetime
import itchat
PROTOCOL = "https"
HOST = "www.okex.com/api/futures"
VERSION = "v3/instruments"
TIMEOUT = 10

class OkexBaseClient (object):
    def __init__(self, key, secret, proxies=None):
        self.URL = "{0:s}://{1:s}/{2:s}".format(PROTOCOL, HOST, VERSION)
        self.KEY = key
        self.SECRET = secret
        self.PROXIES = proxies

    @property
    def _nonce(self):
        """
        Returns a nonce
        Used in authentication
        """
        return str(int(time.time() * 1000))

    def _build_parameters(self, parameters):
        # sort the keys so we can test easily in Python 3.3 (dicts are not # ordered)
        keys = list(parameters.keys())
        keys.sort()
        return '&'.join(["%s=%s" % (k, parameters[k]) for k in keys])

    def url_for(self, path, path_arg=None, parameters=None):
        url = "%s/%s" % (self.URL, path)
        # If there is a path_arh, interpolate it into the URL.
        #  In this case the path that was provided will need to have string
        #  interpolation characters in it
        if path_arg:
            url = url % (path_arg)
        # Append any parameters to the URL.
        if parameters:
            url = "%s?%s" % (url, self._build_parameters(parameters))
            return url

    def _sign_payload(self, payload):
        sign = ''
        for key in sorted(payload.keys()):
            sign += key + '=' + str(payload[key]) +'&'
        data = sign+'secret_key='+self.SECRET
        return hashlib.md5(data.encode("utf8")).hexdigest().upper()

    def _convert_to_floats(self, data):
        """
        Convert all values in a dict to floats at first level
        """
        for key, value in data.items():
            data[key] = float(value)
        return data

    def _get(self, url, timeout=TIMEOUT):
        print(url)
        req = requests.get(url, timeout=timeout, proxies=self.PROXIES)
        if req.status_code/100 != 2:
            logging.error(u"Failed to request:%s %d headers:%s", url, req.status_code, req.headers)
        try:
            return req.json()
        except Exception as e:
            logging.exception('Failed to GET:%s result:%s', url, req.text)
            raise e


    def _post(self, url, params=None, needsign=True, headers=None, timeout=TIMEOUT):
        req_params = {'api_key' : self.KEY}
        if params and needsign:
            req_params.update(params)
        req_params['sign'] = self._sign_payload(req_params)

        req_headers = { "Content-type" : "application/x-www-form-urlencoded"}
        if headers:
            req_headers.update(headers)
        logging.info("%s %s", req_headers, req_params)

        req = requests.post(url, headers=req_headers, data=urllib.urlencode(req_params), timeout=TIMEOUT, proxies=self.PROXIES)
        if req.status_code/100 != 2:
            logging.error(u"Failed to request:%s %d headers:%s", url, req.status_code, req.headers)
        try:
            return req.json()
        except Exception as e:
            logging.exception('Failed to POST:%s result:%s', url, req.text)
            raise e


class OkexClient(OkexBaseClient):
    """
    Client for the Okex.com API.
    See https://www.okex.com/rest_api.html for API documentation.
    """
    def ticker(self, path, start, end, granularity):
        return self._get(self.url_for(path, parameters={'start' : start, 'end' : end, 'granularity' : granularity}))



def isoformat(time):
    '''
    将datetime或者timedelta对象转换成ISO 8601时间标准格式字符串
    :param time: 给定datetime或者timedelta
    :return: 根据ISO 8601时间标准格式进行输出
    '''
    if isinstance(time, datetime.datetime): # 如果输入是datetime
        return time.isoformat();
    elif isinstance(time, datetime.timedelta): # 如果输入时timedelta，计算其代表的时分秒
        hours = time.seconds // 3600
        minutes = time.seconds % 3600 // 60
        seconds = time.seconds % 3600 % 60
    return 'P%sDT%sH%sM%sS' % (time.days, hours, minutes, seconds) # 将字符串进行连接


# wroom
'''
def sendMsgToWRoom(msg):
    print(msg)
    wroom = 'OKEX'
    iRoom = itchat.search_chatrooms(wroom)
    for room in iRoom:
        if room['NickName'] == wroom:
            userName = room['UserName']
            itchat.send_msg(msg, userName)
            break
'''
# wchat
def sendMsgToWChat(msg):
    print(msg)
    wchatList = ['东方云溪']
    for wchat in wchatList:
        users = itchat.search_friends(name=wchat)
        userName = users[0]['UserName']
        itchat.send(msg, toUserName=userName)


PERCENT_TIP = []
#percent
def do_percent(res,name):
    global PERCENT_TIP
    cnt, hights, lows, firstkey = 1, [], [], None
    for val in res:
        if firstkey == None:
            firstkey = val[0]
        hights.append(float(val[2]))
        lows.append(float(val[3]))
        cnt = cnt + 1
        if cnt > 5:
            break

    hmax = float(max(hights))
    lmin = float(min(lows))
    percent = float((hmax - lmin) / lmin * 100)
    if percent >= 2:
        if firstkey in PERCENT_TIP:
            return
        PERCENT_TIP.append(firstkey)
        if len(PERCENT_TIP) > 2:
            del PERCENT_TIP[-1]
        sendMsgToWChat('提醒: [' + name +'] 五分钟之内涨跌幅超过2%!')


if __name__ == "__main__":
    PATH = ["EOS-USD-190927/candles", "BTC-USD-190927/candles"]
    itchat.auto_login(hotReload=True)
    client = OkexClient(None, None)
    subdelta = datetime.timedelta(hours=8)
    while True:
        dtnow = datetime.datetime.now() - subdelta   # utc时间,减8H
        delta = datetime.timedelta(minutes=5)
        start = isoformat(dtnow - delta)
        end = isoformat(dtnow)
        for path in PATH:
            res = client.ticker(path, start[:-6] + '00Z', end[:-6] + '00Z', 60)
            if len(res) > 0:
                do_percent(res, path[:14])
        time.sleep(60)


