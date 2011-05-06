import httplib
from xml.dom import minidom
from libblah.consts import PROTOCOL_VERSION
from libblah.log import logger
from libblah.store import save_data_to_local_json, get_data_from_local_json
from libblah.http import HTTPResponse
from libblah.utils import map_config_xml_to_obj, map_dict_to_obj


def i_update_user_after_get_sys_config_success(user, body):
    body_dom = minidom.parseString(body)
    config = user.get_config()

    node_name_list = ["servers", "parameters", "hints"]
    map_config_xml_to_obj(config, body_dom, node_name_list)

    servers_nodes = body_dom.getElementsByTagName("servers")
    if servers_nodes:
        servers_node = servers_nodes[0]
        config.servers_version = servers_node.getAttribute("version")

    parameters_nodes = body_dom.getElementsByTagName("parameters")
    if parameters_nodes:
        parameters_node = parameters_nodes[0]
        config.parameters_version = parameters_node.getAttribute("version")

    hints_nodes = body_dom.getElementsByTagName("hints")
    if hints_nodes:
        hints_node = hints_nodes[0]
        config.hints_version = hints_node.getAttribute("version")

    data = config.to_dict()
    data.update({"sid" : user.sid})
    save_data_to_local_json(data, "sys_config.json")
    

_GET_SYS_CONFIG_BODY_TPL = '''<?xml version="1.0"?>
<config>
    <user %s="%s"/>
    <servers version="%s"/>
    <parameters version="%s"/>
    <hints version="%s"/>

    <client type="%s" version="%s" platform="%s"/>
</config>'''

def i_download_sys_config(user, debug = False):
    host = "nav.fetion.com.cn"

    httplib.HTTPConnection.response_class = HTTPResponse
    conn = httplib.HTTPConnection(host)
    if debug:
            debuglevel = 1
    else:
        debuglevel = 0
    conn.set_debuglevel(debuglevel)

    account = None
    account_no = None
    if user.get_login_with() == user.LOGIN_WITH_MOBILE_NO:
        account = "mobile-no"
        account_no = user.mobile_no
    elif user.get_login_with() == user.LOGIN_WITH_SID:
        account = "sid"
        account_no = user.sid

    config = user.get_config()

    body_data = (account, account_no,
        config.servers_version or "",
        config.parameters_version or "",
        config.hints_version or "",
            "PC", PROTOCOL_VERSION, "W5.1",)

    body = _GET_SYS_CONFIG_BODY_TPL % body_data

#    headers = {"User-Agent" : "IIC2.0/PC %s" % PROTOCOL_VERSION}
    headers = {"Accept-Encoding" : "compress, gzip"}
    conn.request("POST", "/nav/getsystemconfig.aspx", body, headers)

    res_obj = conn.getresponse()
    conn.close()

    return res_obj


class Config:
    def __init__(self):
        self.servers_version = None
        self.parameters_version = None
        self.hints_version = None

#        self.sipc_proxy_ip = None   # sipc proxy server`s ip
#        self.sipc_proxy_port = None    # sipc proxy server`s port
#
#        self.portrait_server_name = None  # portrait server`s hostname
#        self.portrait_server_path = None  # portrait server`s path , such as /HD_POOL8
#
#        self.icon_size = 25      # portrait`s display size default 25px
#        self.close_alert = None      # whether popup an alert when quiting
#        self.auto_reply = None      # whether auto reply enabled
#        self.is_mute = None
#        self.auto_reply_message = None   # auto reply message content
#        self.msg_alert = None
#        self.auto_popup = None      # whether auto pupup chat dialog enable
#        self.send_mode = None      # press enter to send message or ctrl + enter
#        self.close_mode = None      # close button clicked to close window or show in tray icon it
#        self.can_notify = None
#        self.all_high_light = None
#
#        self.auto_away = None
#        self.auto_away_timeout = None
#
#        self.online_notify = None
#        self.close_sys_msg = None
#        self.close_fetion_show = None
#
#        self.window_width = None
#        self.window_height = None
#        self.window_pos_x = None
#        self.window_pos_y = None
#
#        self.servers_version = None  # the version of some related servers such as sipc server
#        self.parameters_version = None
#        self.hints_version = None  # the version of hints
#
#        self.user_list = None    # user list stored in local data file
#        self.proxy = None      # structure stores the global proxy information

    def to_dict(self):
        d =  {}
        for key, val in self.__dict__.iteritems():
            if not key.startswith("_"):
                d[key] = val
        return d

def load_sys_config_from_local_json(user):
    if user.sid:
        sys_config = get_data_from_local_json(user.sid, "sys_config.json")
        if sys_config:
            logger.info("local sys_config.json found")
            config = user.get_config()
            map_dict_to_obj(sys_config, config)
