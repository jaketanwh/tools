import requests
import itchat

KEY = '********************'  # KEY为图灵机器人的api密钥，自己可以去官网申请


def get_response(msg):
    apiUrl = 'http://www.tuling123.com/openapi/api'
    data = {
        'userid': 'wechat-robot',
        'key': KEY,
        'info': msg,
    }
    try:
        r = requests.post(apiUrl, data=data).json()
        return r.get('text')
    except:
        return


@itchat.msg_register(itchat.content.TEXT)
def tuling_reply(msg):
    defaultReply = 'I received: ' + msg['Text']
    reply = get_response(msg['Text'])
    return reply or defaultReply


itchat.auto_login(hotReload=True)
itchat.run()