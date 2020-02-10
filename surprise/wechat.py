import itchat
import json

def loadmsg():
    file = open("msg.txt", encoding='utf-8')
    msg = json.load(file)
    msgs = {}
    for each in msg:
        msgs[each['question']] = each['answer']
    return msgs

wechatMsgs = loadmsg()

@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    reply = wechatMsgs.get(msg["Text"])
    if reply == None:
        reply = '请换个问题'
    itchat.send_msg(reply, msg['FromUserName'])

itchat.auto_login(True)
itchat.run()