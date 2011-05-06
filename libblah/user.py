from glob import glob
import hashlib
from pprint import pprint as pp
import os
from libblah.consts import get_user_config_path, HASHED_PREFIX
from libblah.consts import HOME_DOMAIN, UserPresence
from libblah.contact import AbstractContact, Contact, GroupAgent, Group
from libblah.log import logger
from libblah.store import get_data_from_local_json, get_account_basic_info_by_account_no
#from libblah.store import delete_config_from_local_json
from libblah.utils import map_dict_to_obj
from libblah.config import Config, load_sys_config_from_local_json

osp = os.path


class User(AbstractContact):
    LOGIN_WITH_MOBILE_NO = 0
    LOGIN_WITH_SID = 1
    def __init__(self, account, hashed_passwd, presence = UserPresence.ONLINE):
        AbstractContact.__init__(self)
        self.version = None
        self.contact_list_version = None
        self.custom_config_version = None

        self._set_login_with(account)
        self._hashed_passwd = hashed_passwd
        self.set_presence(presence)

        self._config = None
        self._ssi_cookie = None
        self._conversations_d = {}
        self._unack_msg_list = []
        self._verification = None

        self._global_call_id = 1
        self._sock = None # SIPC auth socket
        self._group = None
        self._group_agent = None

    def get_presence(self):
        return self._presence

    def set_presence(self, presence):
        self._presence = presence

    def get_sock(self):
        return self._sock

    def set_sock(self, sock):
        self._sock = sock

    def get_config(self):
        return self._config

    def set_config(self, config):
        self._config = config

    def append_to_unack_msg_list(self, unack_msg):
        self._unack_msg_list.append(unack_msg)

    def get_conversations(self):
        return self._conversations_d

    def set_conversations(self, convs):
        self._conversations_d = convs

    def set_user_path(self, sid):
        # $HOME/.fetion/sid
        self._user_path = os.path.join(get_user_config_path(), sid)
        if not os.path.exists(self._user_path):
            os.mkdir(self._user_path)

    def set_portrait_save_path(self):
        # $HOME/.fetion/$SID/portraits/$SID.$MIME_FORMAT
        self._portrait_save_path = os.path.join(self._user_path, "portraits")
        if not os.path.exists(self._portrait_save_path):
            os.mkdir(self._portrait_save_path)

    def get_portrait_save_path(self):
        return self._portrait_save_path

    def get_portrait_path(self):
        path = os.path.join(self.get_user_path(), "%s.*" % self.sid)
        files = glob(path)
        if files:
            portrait_path = glob(path)[0]
            return portrait_path

    def _set_login_with(self, account):
        IS_MOBILE_NO = 11
        if len(account) == IS_MOBILE_NO:
            self.mobile_no = account
            self._login_with = self.LOGIN_WITH_MOBILE_NO
        else:
            self.sid = account
            self._login_with = self.LOGIN_WITH_SID

    def get_login_with(self):
        return self._login_with

    def to_contact(self):
        contact = Contact(user = self)
        for i in contact.__dict__.keys():
            if i in self.__dict__:
                setattr(contact, i, self.__dict__[i])
        return contact

    def get_hashed_passwd(self):
        return self._hashed_passwd

    def get_email(self):
        """ Deprecated for removal in next version """
        return ""

    def get_user_path(self):
        return self._user_path

    def set_ssi_cookie(self, ssi_cookie):
        self._ssi_cookie = ssi_cookie

    def get_ssi_cookie(self):
        return self._ssi_cookie

    def get_global_call_id(self, increase = True):
        call_id = self._global_call_id
        if increase:
            self._global_call_id += 1
        return call_id


def i_hash_passwd(passwd):
    if passwd.startswith(HASHED_PREFIX) and (len(passwd) == (len(HASHED_PREFIX) + 40)):
        return passwd[len(HASHED_PREFIX):]

    t = "%s:%s" % (HOME_DOMAIN, passwd)
    return hashlib.sha1(t).hexdigest()

def i_create_user(account, hashed_passwd, presence):
    user = User(account, hashed_passwd, presence)
    config = Config()
    user.set_config(config)

    load_user_data_from_local_json(account, user)
    load_sys_config_from_local_json(user)
    return user

def update_personal_node_from_local_config(user, personal_config):
    config = user.get_config()
    for key, val in personal_config.iteritems():
        if hasattr(user, key):
            setattr(user, key, val)
        elif hasattr(config, key):
            setattr(config, key, val)

def load_user_data_from_local_json(account_no, user):
    account = get_account_basic_info_by_account_no(account_no)
    if not account:
        logger.error("local personal config not found")
        return
    # there is basic account data, it is not the first time sign in
    sid = account["sid"]

    user_info_versions = get_data_from_local_json(sid, "user_info_versions.json")
    if user_info_versions:
        logger.info("local user_info_versions.json found")
        user.version = user_info_versions["version"]
        user.custom_config_version = user_info_versions["custom_config_version"]
        user.contact_list_version = user_info_versions["contact_list_version"]
    else:
        #delete_config_from_local_json(sid, "user_info_versions.json")
        return

    user.set_user_path(sid)
    user.set_portrait_save_path()

    # get from SIPC auth response body, results -> user-info -> personal node
    personal_node = get_data_from_local_json(sid, "personal_node.json")
    if personal_node:
        update_personal_node_from_local_config(user, personal_node)
#    update_personal_node_from_local_config(user, personal_config)

    custom_config = get_data_from_local_json(sid, "custom_config_node.json")
    if custom_config:
        user.custom_config_version = custom_config["data"]

    # results -> user-info > buddy-list node
    group_data = get_data_from_local_json(sid, "group_list_node.json")
    group_agent = GroupAgent()

    if group_data:
        groups_d = group_data["groups"]
        for gid, gname in groups_d.iteritems():
            group = Group(gid, gname)
            #group = Group(int(gid), gname)
            group_agent.add_group(group)

        for gid, gname in groups_d.iteritems():
            cat_datas = get_data_from_local_json(sid, "%s_list.json" % gname)
            cats_d = cat_datas["contacts"]
            for cat_d in cats_d.values():
                cat = Contact(user)
                map_dict_to_obj(cat_d, cat)
                group_agent.add_contact(cat)

    user.group_agent = group_agent
