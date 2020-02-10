import time,requests,logging,urllib,hashlib,datetime
import itchat,smtplib,os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#from config import EmailConfig

#--------------------自定义参数--------------------
#监测品种 多个品种配置 ["ETH-USDT-200327","BTC-USDT-200327"]
G_PATH = ["ETH-USDT-200327"]

#总时长(分钟)
G_TLEN = 30

#幅度(2%)
G_PERCENT = 2

#微信推送列表
#G_WCHATLIST = ['兰明海']

#邮件服务器地址
G_MAIL_HOST = 'smtp.qq.com'

#smtp端口号
G_MAIL_PORT = 465

#邮箱账号密码
G_MAIL_USER = '1073341020'
G_MAIL_PASSWORD = 'hphryrghxuyibcie'

#发送者邮箱账号
G_MAIL_SENDER = '1073341020@qq.com'

#接受者邮箱账号列表 ['987654321@qq.com','123456789@qq.com']
G_MAIL_RECEIVE_LIST = ['1073341020@qq.com']

#-------------------------------------------------


#--------------------okey-------------------------
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
        try:
            req = requests.get(url, timeout=timeout, proxies=self.PROXIES)
        except Exception as e:
            print('Timeout to GET:' + url)
            return []

        if req.status_code/100 != 2:
            print("Failed to request:" + url + " " + req.status_code,  + " headers:" + req.headers)
            return []
        try:
            return req.json()
        except Exception as e:
            print('Failed to GET:' + url + " cose:" + str(req.status_code))
            return []

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

#-------------------------------------------------

#--------------------wchat------------------------

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
    global G_WCHATLIST
    for wchat in G_WCHATLIST:
        users = itchat.search_friends(name=wchat)
        if users[0] != None:
            userName = users[0]['UserName']
            itchat.send(msg, toUserName=userName)
        else:
            print('微信好友' + wchat + '未找到')
#-------------------------------------------------


#--------------------mail-------------------------
class SendEmail(object):
    """
    smtp邮件功能封装
    """
    def __init__(self, host: str='', user: str='', password: str='', port: int='', sender: str='', receive: list=''):
        """
        :param host: 邮箱服务器地址
        :param user: 登陆用户名
        :param password: 登陆密码
        :param port: 邮箱服务端口
        :param sender: 邮件发送者
        :param receive: 邮件接收者
        """
        self.HOST = host
        self.USER = user
        self.PASSWORD = password
        self.PORT = port
        self.SENDER = sender
        self.RECEIVE = receive

        # 与邮箱服务器的连接
        self._server = ''
        # 邮件对象,用于构造邮件内容
        self._email_obj = ''

    def load_server_setting_from_obj(self, obj):
        """从对象中加载邮件服务器的配置
        :param obj, 类对象
        HOST, 邮件服务器地址
        USER, 邮件服务器登陆账号
        PASSWORD, 邮件服务器登陆密码
        SENDER, 发送者
        """
        attrs = {key.upper(): values for key, values in obj.__dict__.items() if not key.startswith('__')}
        for key, value in attrs.items():
            self.__setattr__(key, value)

    def connect_smtp_server(self, method='default'):
        """连接到smtp服务器"""
        if method == 'default':
            self._server = smtplib.SMTP(self.HOST, self.PORT, timeout=2)
        if method == 'ssl':
            self._server = smtplib.SMTP_SSL(self.HOST, self.PORT, timeout=2)
        try:
            self._server.login(self.USER, self.PASSWORD)
        except Exception as e:
            print('Timeout login mail')
            return False
        return True

    def construct_email_obj(self, subject='python email'):
        """构造邮件对象
        subject: 邮件主题
        from: 邮件发送方
        to: 邮件接收方
        """

        # mixed参数表示混合类型，这个邮件对象可以添加html,txt,附件等内容
        msg = MIMEMultipart('mixed')
        msg['Subject'] = subject
        msg['From'] = self.SENDER
        msg['To'] = ';'.join(self.RECEIVE)
        self._email_obj = msg

    def add_content(self, content: str, _type: str = 'txt'):
        """给邮件对象添加正文内容"""
        if _type == 'txt':
            text = MIMEText(content, 'plain', 'utf-8')
        if _type == 'html':
            text = MIMEText(content, 'html', 'utf-8')

        self._email_obj.attach(text)

    def add_file(self, file_path: str):
        """
        给邮件对象添加附件
        :param file_path: 文件路径
        :return: None
        """
        # 构造附件1，传送当前目录下的 test.txt 文件
        email_file = MIMEText(open(file_path, 'rb').read(), 'base64', 'utf-8')
        email_file["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        file_name = os.path.basename(file_path)
        # 下面这种写法，如果附件名是中文，会出现乱码问题，修改成如下写法
        # email_file["Content-Disposition"] = f'attachment; filename="{file_name}"'
        email_file.add_header("Content-Disposition", "attachment", filename=file_name)
        self._email_obj.attach(email_file)

    def send_email(self):
        """发送邮件"""
        # 使用send_message方法而不是sendmail,避免编码问题
        try:
            self._server.send_message(from_addr=self.SENDER, to_addrs=self.RECEIVE, msg=self._email_obj)
        except Exception as e:
            print('Timeout send mail')
            return False
        return True

    def quit(self):
        self._server.quit()

    def close(self):
        self._server.close()

# mail
def sendMsgToMail(msg):
    print(msg)
    global G_MAIL_HOST,G_MAIL_PORT,G_MAIL_USER,G_MAIL_PASSWORD,G_MAIL_SENDER,G_MAIL_RECEIVE_LIST
    try:
        email = SendEmail(G_MAIL_HOST, G_MAIL_USER, G_MAIL_PASSWORD, G_MAIL_PORT, G_MAIL_SENDER, G_MAIL_RECEIVE_LIST)
        ret = email.connect_smtp_server(method='ssl')
        if not ret:
            email.close()
            return
        email.construct_email_obj(subject='okey提醒' + str(time.strftime('%Y/%m/%d %H:%M')))
        email.add_content(content=msg)
        email.send_email()
        email.close()
    except Exception as e:
        print('Fail to sendMsgToMail')
        return

#-------------------------------------------------

#-------------------------------------------------
#percent
PERCENT_TIP = {}
def do_percent(res,name):
    global PERCENT_TIP,G_PERCENT,G_TLEN
    cnt, hights, lows = 1, [], []
    for val in res:
        high = float(val[2])
        low = float(val[3])
        hights.append(high)
        lows.append(low)
        cnt = cnt + 1
        if cnt > 5:
            break

    hmax = float(max(hights))
    lmin = float(min(lows))
    percent = float((hmax - lmin) / lmin * 100)
    print('监测幅度:' + str(percent) + ' 最高价:' + str(hmax) + ' 最低价:' + str(lmin))
    if percent >= G_PERCENT:
        now = time.time()
        if PERCENT_TIP[path] > now:
            return
        PERCENT_TIP[path] = now + G_TLEN * 60
        msg = 'Okex推送: [' + name +']' + str(G_TLEN) + '分钟之内涨跌幅超过' + str(round(percent, 2)) + '%!'
        #sendMsgToWChat(msg)
        sendMsgToMail(msg)

if __name__ == "__main__":
    #itchat.auto_login()#hotReload=True
    client = OkexClient(None, None)
    subtm = datetime.timedelta(hours=8)
    for path in G_PATH:
        PERCENT_TIP[path] = 0
    while True:
        dtnow = datetime.datetime.now() - subtm
        stm = isoformat(dtnow - datetime.timedelta(minutes = G_TLEN))
        etm = isoformat(dtnow)
        for path in G_PATH:
            res = client.ticker(path + "/candles", stm[:-6] + '00Z', etm[:-6] + '00Z', 60)
            if len(res) > 0:
                do_percent(res, path)
        time.sleep(60)


