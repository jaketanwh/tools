import sys
sys.path.append('data')
sys.path.append('tool')
sys.path.append('surprise')
sys.path.append('dog')
import data,surprise,dog
import tools
import time

MAIN_RESET_CONTROL = False                          #今日是否更新开关
MAIN_ISOPEN_DAY = tools.gettodaytrade()             #今日是否开盘
MAIN_WEEKDAY = -1                                   #今日是周几
MAIN_DATA_UPDATA = True                             #每日更新db
MAIN_REPLAY_SURPRISE = True                         #每日复盘

###############################################################################################
# update
###############################################################################################

#更新db数据
def downdb():
    global MAIN_DATA_UPDATA
    if not MAIN_DATA_UPDATA:
        return
    MAIN_DATA_UPDATA = False
    data.start()

#web
def surprise():
    global MAIN_REPLAY_SURPRISE
    if not MAIN_REPLAY_SURPRISE:
        return
    MAIN_REPLAY_SURPRISE = False
    surprise.start()

#dog
def dog_init():
    dog.start()

def dog():
    dog.update()

def update():
    # 交易日判定
    if MAIN_ISOPEN_DAY == 0:
        return

    # 北京时间
    bjtime, weekday = tools.get_servertime()
    if bjtime == -1 or weekday == -1:
        return

    hour = bjtime.tm_hour
    minute = bjtime.tm_min
    second = bjtime.tm_sec

    if hour == 9 and minute > 14 and minute < 26:
        #竞价
        print('1')
    elif hour == 9 and minute == 25 and second > 10 and second < 20:
        #计算竞价
        print('1')
    elif (hour == 9 and minute > 29) or (hour > 9 and hour < 11) or (hour == 11 and minute < 32) or (hour > 12 and hour < 15) or (hour == 15 and minute < 2):
        #盘中
        dog()
    elif hour == 0 and minute > 10 and minute < 20:
        #每日重置
        do_reset()
    elif hour == 18 and minute < 10:
        #每日更新数据
        downdb()
    #elif hour == 19 and minute < 30:
        #每日复盘
        #surprise()

    #新闻

    time.sleep(3)

def do_while():
    while True:
        update()

def do_reset():
    global MAIN_WEEKDAY
    week = -1
    while week == -1:
        _, week = tools.get_servertime()
    if week == MAIN_WEEKDAY:
        return
    MAIN_WEEKDAY = week

    global MAIN_DATA_UPDATA,MAIN_REPLAY_SURPRISE,MAIN_ISOPEN_DAY
    MAIN_DATA_UPDATA = True
    MAIN_REPLAY_SURPRISE = True
    MAIN_ISOPEN_DAY = tools.gettodaytrade()

###############################################################################################
# main
###############################################################################################

def main_init():
    print('[Main] init')
    global MAIN_WEEKDAY
    week = -1
    while week == -1:
        _, week = tools.get_servertime()
    MAIN_WEEKDAY = week

def main_destroy():
    print('[Main] destroy')

if __name__ == "__main__":
    main_init()
    #dog_init()
    #do_while()
    downdb()
    main_destroy()
