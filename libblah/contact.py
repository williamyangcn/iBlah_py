"""
CURD item of contact list.
"""
from glob import glob
from xml.dom import minidom
import os
from libblah.consts import DEFAULT_SIP_SEQUENCE, YES, UserPresence, NO
from libblah.sip import SIPConnection, SIPEvent, SIP
from libblah.strutils import to_unicode_obj


class GroupAgentItemType:
    GROUP = 1
    CONTACT = 2


class Group:
    def __init__(self, gid, gname, contacts_list = None):
        self._type = GroupAgentItemType.GROUP
        self.gid = gid
        self.gname = gname
        self.contact_list = []

        if contacts_list:
            for contact in contacts_list:
                self.add_contact(contact)

    def add_contact(self, cat):
        if cat not in self.contact_list:
            cat.set_group(self)
            self.contact_list.append(cat)

    def count(self):
        return len(self.contact_list)

    def get_contact_by_row(self, row):
        return self.contact_list[row]

    def get_contact_by_uri(self, uri):
        for contact in self.contact_list:
            if contact.uri == uri:
                return contact

    def get_contact_by_user_id(self, user_id):
        for contact in self.contact_list:
            if contact.user_id == user_id:
                return contact

    def get_type(self):
        return self._type

    def get_display_name(self):
        return u"%s [%d/%d]" % (self.gname, self.get_online_count(), self.count())

    def get_online_count(self):
        count = 0
        for contact in self.contact_list:
            if contact.presence > UserPresence.OFFLINE_OR_INVISIBLE:
                count += 1
        return count

    def delete_contact(self, contact):
        self.contact_list.remove(contact)

    def sort(self):
        self.contact_list = sorted(self.contact_list,
                                   key = lambda contact: contact.presence, reverse = True)


class GroupAgent:
    def __init__(self, groups = None):
        self.group_list = []

        if groups:
            for group in groups:
                self.add_group(group)

    def add_group(self, group):
        self.group_list.append(group)

    def add_contact(self, contact):
        gid = contact.gid
        group = self.get_group_by_id(gid)
        group.add_contact(contact)

    def count(self):
        return len(self.group_list)

    def get_group_by_row(self, row):
        return self.group_list[row]

    def get_group_by_id(self, gid):
        for group in self.group_list:
            if group.gid == gid:
                return group

    def index(self, group):
        return self.group_list.index(group)

    def get_contact_by_uri(self, uri):
        for group in self.group_list:
            contact = group.get_contact_by_uri(uri)
            if contact:
                return contact

    def get_contact_by_user_id(self, user_id):
        for group in self.group_list:
            contact = group.get_contact_by_user_id(user_id)
            if contact:
                return contact

    def get_all_contacts(self):
        contacts_list = []
        for group in self.group_list:
            contacts_list.extend(group.contact_list)
        return contacts_list

    def delete_user_by_user_id(self, user_id):
        for group in self.group_list:
            contact = group.get_contact_by_user_id(user_id)
            if contact:
                group.delete_contact(contact)
                return

    def delete_contact_by_uri(self, uri):
        for group in self.group_list:
            contact = group.get_contact_by_uri(uri)
            if contact:
                group.delete_contact(contact)
                return

    def sort(self):
        for group in self.group_list:
            group.sort()


class AbstractContact():
    def __init__(self):
        self.birthday_valid = None
        self.carrier = None
        self.carrier_region = None
        self.carrier_status = None
        self.email_binding_alias = None

        self.gender = None
        self.impresa = None
        self.mobile_no = None
        self.name = None
        self.nickname = None

        self.portrait_crc = None
        self.sid = None
        self.uri = None
        self.user_id = None
        self.user_region = None

        self.version = None

        # addition attributes
        self._type = GroupAgentItemType.CONTACT
        self.presence = UserPresence.OFFLINE_OR_INVISIBLE

    def get_name(self):
        return u"%s %s" % (self.name or "", self.nickname or "")

    def get_display_name(self):
        if self.nickname and self.nickname.strip():
            return u"%s (%s) " % (to_unicode_obj(self.nickname), self.sid)
        elif self.mobile_no and self.mobile_no.strip():
            return u"%s (%s) " % (self.mobile_no, self.sid)
        else:
            return u"%s" % self.sid

    def get_type(self):
        return self._type

    def to_dict(self):
        d =  {}
        for key, val in self.__dict__.iteritems():
            if not key.startswith("_"):
                d[key] = val
        return d


class Contact(AbstractContact):
    def __init__(self, user):
        AbstractContact.__init__(self)

        self.service_status = None
        self.birth_date = None
        self.blood_type = None
        self.hobby = None
        self.home_phone = None

        self.horoscope = None
        self.identity = None # whether to show mobile No. to this user
        self.lunar_animal = None
        self.occupation = None
        self.other_email = None

        self.other_phone = None
        self.personal_email = None
        self.primary_email = None
        self.profile = None
        self.relation_status = None # this value set after someone

        self.score_level = None
        # self.version = None
        self.work_email = None
        self.work_phone = None

        self._init_addition_attrs()
        self._user = user

    def _init_addition_attrs(self):
        self.image_changed = None
        self.device_type = None

        #
        # system will push following data after someone add use as friend
        #
#        self._buddy_lists = None
#        self.gid = self._buddy_lists # se do use gid instead of later
        self.gid = None
        self.online_notify = None
        self.permission_values = None

    def set_gid(self, gid):
        self.gid = gid
        #self._buddy_lists = gid

    def set_group(self, group):
        self._group = group

    def get_group(self):
        return self._group

    def get_email(self):
        print "PRIMARY\tOTHER"
        print "%s\t%s" % (self.primary_email or "", self.other_email or "")
        print "PERSONAL\tWORK"
        print "%s\t%s" % (self.personal_email or "", self.work_email or "")
        return ""

    def get_portrait_path(self):
        path = os.path.join(self._user.get_portrait_save_path(), "%s.*" % self.sid)
        files = glob(path)
        if files:
            portrait_path = glob(path)[0]
            return portrait_path

        
def i_subscribe_contact_list(user, debug = False):
    from_sid = user.sid
    call_id = user.get_global_call_id()

    sip_type = SIP(SIP.SUBSCRIPTION)
    sip_event = SIPEvent(SIPEvent.PRESENCE_V4)

    headers = dict({
        "F" : from_sid,
        "I" : str(call_id),
        "Q" : "%d %s" % (DEFAULT_SIP_SEQUENCE, str(sip_type)),

        "N" : str(sip_event),
        })

    body = '''<args><subscription self="v4default;mail-count" buddy="v4default" version="0"/></args>'''
    sip_conn = SIPConnection(user.get_sock(), sip_type = sip_type,
                             headers = headers, body = body)
    sip_conn.send(recv = False, debug = debug)

_ADD_BUDDY_TPL = """<args>
    <contacts>
        <buddies>
            <buddy uri="mix:%s" buddy-lists="%s" desc="%s" expose-mobile-no="%s"
                expose-name="%s" addbuddy-phrase-id="%d" />
        </buddies>
    </contacts>
</args>"""

def i_add_buddy(user, account, myname, debug = False):
    call_id = str(user.get_global_call_id())

    sip_type = SIP(SIP.SERVICE)
    from_sid = user.sid
    sip_event = str(SIPEvent(SIPEvent.ADD_BUDDY_V4))

    headers = {
        "F" : from_sid,
        "I" : call_id,
        "Q" : "1 %s" % sip_type,
        "N" : sip_event,
    }

    buddy_list_name = ""
    desc = myname
    expose_mobile_no = YES
    expose_name = YES
    add_buddy_phrase_id = 0

    body = _ADD_BUDDY_TPL % \
           (account, buddy_list_name, desc, expose_mobile_no, expose_name, add_buddy_phrase_id)
    sip_conn = SIPConnection(user.get_sock(), sip_type = sip_type, headers = headers, body = body)
    sip_conn.send(recv = False, debug = debug)

    """ TODO:
    We need add this message to un-ack message list,
    we should update contact list after get accept reply. """


def i_parse_add_buddy_refused(body_dom):
    app_node = body_dom.getElementsByTagName("application")[0]
    attr = app_node.getAttribute

    #user_id = attr("user-id")
    uri = attr("uri")
    reason = attr("reason")
    return (uri, reason)

def i_parse_add_buddy_application(body_dom):
    app_node = body_dom.getElementsByTagName("application")[0]
    attr = app_node.getAttribute

    data = {
        "uri" : attr("uri"),
        "who" : to_unicode_obj(attr("desc")),
        "add_buddy_phrase_id" : int(attr("addbuddy-phrase-id")),
        "user_id" : attr("user-id")
    }
    #type = attr("type")
    return data


_REPLY_ACCEPT_FOR_ADD_BUDDY_TPL = """<args>
<contacts>
    <buddies><buddy user-id="%s" result="%d" buddy-lists="%s" local-name="%s"
        expose-mobile-no="%d" expose-name="%d" /></buddies>
</contacts>
</args>"""

_REPLY_IGNORE_FOR_ADD_BUDDY_TPL = """<args>
<contacts><buddies><buddy user-id="%s" result="%d" /></buddies></contacts>
</args>"""


_REPLY_REFUSE_FOR_ADD_BUDDY_TPL = """<args>
    <contacts>
        <buddies>
            <buddy user-id="%s" result="%d" accept-instant-message="%d"
                expose-basic-presence="%d" reason="%s" />
        </buddies>
        </contacts>
</args>"""


class ReplyAddBuddyApplication:
    REFUSE = 0
    ACCEPT = 1
    IGNORE = 2


def i_reply_add_buddy(user, res_obj, result, refuse_reason,
                      decline_add_req_forever, debug = False):

    body_dom = minidom.parseString(res_obj.body)
    app_data = i_parse_add_buddy_application(body_dom)

    #attr = res_obj.headers.get_field_value

    call_id = user.get_global_call_id()

    from_sid = user.sid
    sip_type = SIP(SIP.SERVICE)
    sip_event = SIPEvent(SIPEvent.HANDLE_CONTACT_REQUEST_V4)

    headers = {
        "F" : from_sid,
        "I" : str(call_id),
        "Q" : "1 %s" % (str(sip_type)),
        "N" : str(sip_event)
        }

    if result == ReplyAddBuddyApplication.ACCEPT:
        buddy_list_id = 0
        local_name = ""
        expose_mobile_no = YES
        expose_name = YES
        body = _REPLY_ACCEPT_FOR_ADD_BUDDY_TPL % (app_data["user_id"], result, buddy_list_id,
                                                 local_name, expose_mobile_no, expose_name)

    elif result == ReplyAddBuddyApplication.REFUSE:
        if decline_add_req_forever:
            accept_instant_message = NO
        else:
            accept_instant_message = YES
        expose_basic_presence = UserPresence.OFFLINE_OR_INVISIBLE
        body = _REPLY_REFUSE_FOR_ADD_BUDDY_TPL % (app_data["user_id"], result,
                accept_instant_message, expose_basic_presence, refuse_reason)

        if decline_add_req_forever:
            i_add_to_black_list(user, app_data["uri"], app_data["who"], debug = True)

    elif result == ReplyAddBuddyApplication.IGNORE:
        body = _REPLY_IGNORE_FOR_ADD_BUDDY_TPL % (app_data["user_id"], result)

    sip_conn = SIPConnection(user.get_sock(), sip_type = sip_type, headers = headers, body = body)
    sip_conn.send(recv = False, debug = debug)


_ADD_TO_BLACK_LIST_TPL = """<args>
    <contacts>
        <blacklist>
            <blocked uri="%s" local-name="%s" />
        </blacklist>
    </contacts>
</args>"""

def i_add_to_black_list(user, uri, local_name, debug = False):
    call_id = str(user.get_global_call_id())

    sip_type = SIP(SIP.SERVICE)
    sip_event = SIPEvent(SIPEvent.ADD_TO_BLACK_LIST)
    from_sid = user.sid

    headers = {
        "F" : from_sid,
        "I" : call_id,
        "Q" : "1 %s" % str(sip_type),

        "N" : str(sip_event),
    }

    body = _ADD_TO_BLACK_LIST_TPL % (uri, local_name)

    sip_conn = SIPConnection(user.get_sock(), sip_type = sip_type, headers = headers, body = body)
    sip_conn.send(recv = False, debug = debug)

_DELETE_BUDDY_TPL = """<args>
<contacts><buddies><buddy user-id="%s" delete-both="%d" /></buddies></contacts>
</args>"""

def i_delete_buddy(user, uri, delete_both, debug = True):
    call_id = user.get_global_call_id()

    from_sid = user.sid
    sip_type = SIP(SIP.SERVICE)
    sip_event = SIPEvent(SIPEvent.DELETE_BUDDY_V4)

    target_contact = user.group_agent.get_contact_by_uri(uri)
    user_id = target_contact.user_id

    headers = {
        "F" : from_sid,
        "I" : str(call_id),
        "Q" : "1 %s" % (str(sip_type)),
        "N" : str(sip_event)
        }

    if delete_both:
        delete_me_from_his_contact_list = YES
    else:
        delete_me_from_his_contact_list = NO

    body = _DELETE_BUDDY_TPL % (user_id, delete_me_from_his_contact_list)
    sip_conn = SIPConnection(user.get_sock(), sip_type = sip_type, headers = headers, body = body)
    sip_conn.send(recv = False, debug = debug)

    """ TODO:
        add this request message into un-ack list, delete buddy after get OK response.
    """

    user.group_agent.delete_contact_by_uri(uri)
