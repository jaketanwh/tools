import itchat

MSG_CATCH = []
WCHAT_ROOMNAME = '测试狗'


# wchat
def sendMsgToWChat(msg,wchatList):
    for wchat in wchatList:
        users = itchat.search_friends(name=wchat)
        userName = users[0]['UserName']
        itchat.send(msg,toUserName=userName)

itchat.search_chatrooms(name='LittleCoder')

# wroom
def sendMsgToWRooms(msg,wroomList):
    itchat.get_chatrooms(update=True)
    for wroom in wroomList:
        iRoom = itchat.search_chatrooms(wroom)
        for room in iRoom:
            if room['NickName'] == wroom:
                userName = room['UserName']
                itchat.send_msg(msg, userName)
                break

# wroom
def sendMsgToWRoom(msg):
    global WCHAT_ROOMNAME
    wroom = WCHAT_ROOMNAME
    iRoom = itchat.search_chatrooms(wroom)
    for room in iRoom:
        if room['NickName'] == wroom:
            userName = room['UserName']
            itchat.send_msg(msg, userName)
            break



def update():
    global MSG_CATCH
    if len(MSG_CATCH) == 0:
        return

    for i in range(10):
        sendMsgToWRoom(MSG_CATCH[0])
        MSG_CATCH.pop(0)
        if len(MSG_CATCH) == 0:
            break


def add(msg):
    if msg == None or msg == '':
        return

    global MSG_CATCH
    MSG_CATCH.append(msg)


def start():
    itchat.auto_login(hotReload=True)
    print('[sendmsg] itchat init')


