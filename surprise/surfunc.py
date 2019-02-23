#K线类
class SURKINFO:
    m_open      = 0                 #开盘价
    m_high      = 0                 #最高价
    m_low       = 0                 #最低价
    m_close     = 0                 #收盘价
    m_volume    = 0                 #成交量
    m_amount    = 0                 #成交额

    def __init__(self,open,high,low,close,volume,amount):
        self.m_open = open
        self.m_high = high
        self.m_low = low
        self.m_close = close
        self.m_volume = volume
        self.m_amount = amount

#财务数据
class FUNNYINFO:
    m_hehe      = 0

#数据类
class SURINFO:
    m_sur_k_info        = None          #k线数据
    m_sur_funny_info    = None          #财务数据
    def __init__(self,sur_k_info,sur_funny_info):
        self.m_sur_k_info = sur_k_info
        self.m_sur_funny_info = sur_funny_info