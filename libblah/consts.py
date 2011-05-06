#-*- coding: utf-8 -*-

# string
import os
from time import time

osp = os.path

version = "20110506"
version_info = (2011, 5, 6)

NAME = "iBlah"
DESCRIPTION_ZH_CN = u"%s 是一款免费发即时信息到手机或电脑 Mac OS 客户端；中国移动飞信协议兼容 %s 。" % (NAME, NAME)
DESCRIPTION_EN = "%s is a free software for Mac OS to send instance message to computer or cellphone." % NAME
AUTHOR = 'LeE lI'
AUTHOR_EMAIL = 'flyinflash@gmail.com'
AUTHOR_QQ = "84000424"
AUTHOR_MOBILE_NO = "15818838404"
ABOUT_TITLE = u"关于 %s" % NAME

ABOUT_MSG = u'''<a href="https://bitbucket.org/shugelee/%s/wiki/How-To-Submit-Issue">网页提交 Bugs </a>
<br /><br />
QQ 提交 Bugs: %s
<br /><br />
EMail 提交 Bugs: %s
<br /><br />
短信 提交 Bugs: %s
<br /><br />
%s
<br /><br />
iBlah version %s
<br /><br />
作者： %s <%s>''' % (NAME, AUTHOR_QQ, AUTHOR_EMAIL, AUTHOR_MOBILE_NO,
                  DESCRIPTION_ZH_CN, version, AUTHOR, AUTHOR_EMAIL)

# configuration file path prefix
CONFIG_PATH_PREFIX = '.%s' % NAME.lower()


STR_NOT_FOUND = -1

# SIP
CRLF = "\r\n"
PROTOCOL = "SIP-C/4.0"
PROTOCOL_VERSION = "4.0.2510"
HOME_DOMAIN = "fetion.com.cn"
DEFAULT_SIP_SEQUENCE = 2
SERVICE_PROVIDER_URI = "sip:10000@fetion.com.cn;p=100"

# socket
SOCK_RECV_SIZE_ONCE = 1024

# Fetion protocol
IS_MOBILE_NO = 11
IS_USER_ID = 9
IS_SID = 9

DEFAULT_GID = 0
STRANGER_GROUP_GID = -1
BLACKLIST_GROUP_GID = -2

MAX_RETRY_TIMES = 6
HASHED_PREFIX = "hash!"

YES = 1
NO = 0


class AbstractConst:
    CONST_TO_STR = None
    def __init__(self, const):
        self.const = const

    def __str__(self):
        return self.CONST_TO_STR[self.const]

    @staticmethod
    def get_const_by_str(obj, s):
        for const, string in obj.CONST_TO_STR.iteritems():
            if string == s:
                return const


class UserPresence(AbstractConst):
    OFFLINE = -1 # not for presence
    OFFLINE_OR_INVISIBLE = 0
    AWAY = 100

#    ON_THE_PHONE = 150
#    RIGHT_BACK = 300
#    OUT_FOR_LUNCH = 500
#    BUSY = 600
#    DO_NOT_DISTURB = 800
#    MEETING = 850

    ONLINE = 400

    CONST_TO_STR = {
        OFFLINE_OR_INVISIBLE : "offline",
        AWAY : "away",
        ONLINE : "online",
    }
    CONST_TO_STR_ZH = {
        OFFLINE_OR_INVISIBLE : u"隐身",
        AWAY : u"离开",
        ONLINE : u"在线",
    }

    def get_zh(self, const):
        return self.CONST_TO_STR_ZH[const]

def get_platform():
    import platform
    pl = None
    while not pl:
        try:
            pl = platform.system()
        except:
            # # quick and dirty fix system call failed
            # pl = "Darwin"
            time.sleep(0.1)
            continue    
    return pl

def get_user_config_path():
    home_path = os.getenv("HOME") or os.path.expanduser("~")
    config_path = os.path.join(home_path, CONFIG_PATH_PREFIX)
    if not os.path.exists(config_path):
        os.makedirs(config_path)
    return config_path

def get_desktop_path():
    home_path = os.getenv("HOME") or os.path.expanduser("~")
    return osp.join(home_path, "Desktop")
