import sys
sys.path.append('data')
sys.path.append('tool')
sys.path.append('surprise')
import data,surprise
import tools

MAIN_RESET_CONTROL = False                          #今日是否更新开关
MAIN_DATA_UPDATA = True                             #每日更新db
MAIN_REPLAY_SURPRISE = True                         #每日复盘

###############################################################################################
# update
###############################################################################################

def downdb():
    global MAIN_DATA_UPDATA
    if not MAIN_DATA_UPDATA:
        return
    MAIN_DATA_UPDATA = False
    data.start()

def surprise():
    global MAIN_REPLAY_SURPRISE
    if not MAIN_REPLAY_SURPRISE:
        return
    MAIN_REPLAY_SURPRISE = False
    surprise.start()

def update():
    bjtime, weekday = tools.get_servertime()
    if bjtime == -1 or weekday == -1:
        return

    # 周末去除
    if weekday == 0 or weekday == 6:
        return

    hour = bjtime.tm_hour
    minute = bjtime.tm_min
    second = bjtime.tm_sec

    if hour == 0 and minute < 10:
        #每日重置
        do_reset()
    elif hour == 17 and minute < 10:
        #每日更新数据
        downdb()
    #elif hour == 17 and minute > 30:
        #每日复盘
        #surprise()

'''
   if hour == 9 and minute > 14 and minute < 26:
       #竞价
       jj()
   elif hour == 9 and minute == 26 and second > 0 and second < 10:
       #计算竞价
       jsjj()
   elif hour == 9 and minute == 26 and second > 10 and second < 20:
       #统计每日集合竞价量数据
       jjdb()
   elif (hour == 9 and minute > 30) or (hour > 9 and hour < 11) or (hour == 11 and minute < 32) or (hour == 13 and minute > 1) or (hour > 13 and hour < 15) or (hour == 15 and minute < 2):
       #盘中
       gp()
       '''

def do_while():
    while True:
        update()

def do_reset():
    global MAIN_DATA_UPDATA
    if MAIN_DATA_UPDATA:
        return

    MAIN_DATA_UPDATA = True
###############################################################################################
# main
###############################################################################################

def main_init():
    print('[Main] init')

def main_destroy():
    print('[Main] destroy')
    data.destroy()

if __name__ == "__main__":
    main_init()
    downdb()
    #do_while()
    main_destroy()
