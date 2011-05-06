import errno
import httplib
from pprint import pprint as pp
import re
import sys
import traceback
from xml.dom import minidom
import socket
import time

from libblah.consts import CRLF, STR_NOT_FOUND, SOCK_RECV_SIZE_ONCE, DEFAULT_SIP_SEQUENCE
from libblah.consts import AbstractConst
from libblah.consts import PROTOCOL, HOME_DOMAIN
from libblah.log import logger
from libblah.strutils import strip2, to_byte_str


class NotificationEvent(AbstractConst):
    PRESENCE_CHANGED = 0
    ADD_BUDDY_APPLICATION = 1
    USER_LEFT = 2
    DEREGISTRATION = 3 # `Your fetion has login elsewhere. You are forced to quit`
    SYNC_USER_INFO = 4
    PG_GET_GROUP_INFO = 5

    # conversation
    USER_FAILED = 1000
    SUPPORT = 1001
    USER_ENTERED = 1003

    MOBILE_MAIL_BOX_CHANGED = 1004

    # SystemNotifyV4
    ADD_BUDDY_REFUSED = 1005
    USER_DYNAMICS_CHANGED = 1006

    CONST_TO_STR =  {
        PRESENCE_CHANGED : "PresenceChanged",
        USER_LEFT : "UserLeft",

        SYNC_USER_INFO : "SyncUserInfo",
        ADD_BUDDY_APPLICATION : "AddBuddyApplication",
        PG_GET_GROUP_INFO : "PGGetGroupInfo",

        DEREGISTRATION : "deregistered",

        # conversation
        USER_FAILED : "UserFailed",
        SUPPORT : "Support",
        USER_ENTERED : "UserEntered",

        # notification
        MOBILE_MAIL_BOX_CHANGED : "MobileMailBoxChanged",

        # SystemNotifyV4
        ADD_BUDDY_REFUSED : "AddBuddyRefused",
        USER_DYNAMICS_CHANGED : "UserDynamicsChanged",
        }


class SIPEvent(AbstractConst):
    PRESENCE_V4 = 0
    SET_PRESENCE = 1
    CONTACT = 2
    CONVERSATION = 3
    CAT_MESSAGE = 4 # `cat` means `contact`
    SEND_CAT_MESSAGE = 5
    START_CHAT = 6
    INVITE_BUDDY = 7
    GET_CONTACT_INFO = 8
    CREATE_BUDDY_LIST = 9
    DELETE_BUDDY_LIST = 10
    SET_CONTACT_INFO = 11
    SET_USER_INFO = 12
    SET_BUDDYLIST_INFO = 13
    DELETE_BUDDY_V4 = 14
    ADD_BUDDY_V4 = 15
    KEEP_ALIVE = 16
    DIRECT_SMS = 17
    SEND_DIRECTCAT_SMS = 18
    HANDLE_CONTACT_REQUEST_V4 = 19
    PG_GET_GROUP_LIST = 20
    PG_GET_GROUP_INFO = 21
    PG_GET_GROUP_MEMBERS = 22
    PG_SEND_CAT_SMS = 23
    PG_PRESENCE = 24
    
    SYNC_USER_INFO_V4 = 25
    KEEP_CONNECTION_BUSY = 26

    REGISTRATION = 27
    SYSTEM_NOTIFY_V4 = 28

    # recevie add buddy application
    CONTACT = 29

    ADD_TO_BLACK_LIST = 30

    CONST_TO_STR = {
        PRESENCE_V4 : "PresenceV4",
        SET_PRESENCE : "SetPresenceV4",
        #CONTACT : "CatMsg",
        CONVERSATION : "Conversation",
        CAT_MESSAGE : "CatMsg",
        SEND_CAT_MESSAGE : "SendCatSMS",
        START_CHAT : "StartChat",
        INVITE_BUDDY : "InviteBuddy",
        GET_CONTACT_INFO : "GetContactInfoV4",
        CREATE_BUDDY_LIST : "CreateBuddyList",
        DELETE_BUDDY_LIST : "DeleteBuddyList",
        SET_CONTACT_INFO : "SetContactInfoV4",
        SET_USER_INFO : "SetUserInfoV4",
        SET_BUDDYLIST_INFO : "SetBuddyListInfo",
        DELETE_BUDDY_V4 : "DeleteBuddyV4",

        ADD_BUDDY_V4 : "AddBuddyV4",

        ADD_TO_BLACK_LIST : "AddToBlacklist",

        KEEP_ALIVE : "KeepAlive",
        DIRECT_SMS : "DirectSMS",
        SEND_DIRECTCAT_SMS : "SendDirectCatSMS",
        HANDLE_CONTACT_REQUEST_V4 : "HandleContactRequestV4",
        PG_GET_GROUP_LIST : "PGGetGroupList",
        PG_GET_GROUP_INFO : "PGGetGroupInfo",
        PG_GET_GROUP_MEMBERS : "PGGetGroupMembers",
        PG_SEND_CAT_SMS : "PGSendCatSMS",
        PG_PRESENCE : "PGPresence",
        
        SYNC_USER_INFO_V4 : "SyncUserInfoV4",
        KEEP_CONNECTION_BUSY : "KeepConnectionBusy",
        REGISTRATION : "registration",

        SYSTEM_NOTIFY_V4 : "SystemNotifyV4",

        # receive add buddy application
        CONTACT : "contact",
        }
    

class SIP(AbstractConst):
    REGISTER = 1
    SERVICE = 2
    SUBSCRIPTION = 3
    NOTIFICATION = 4
    INVITATION = 5
    INCOMING = 6
    OPTION = 7
    MESSAGE = 8
    SIPC_4_0 = 9
    ACKNOWLEDGE = 10
    UNKNOWN = 11

    CONST_TO_STR = {
        REGISTER :"R",
        SERVICE : "S",
        SUBSCRIPTION : "SUB",
        NOTIFICATION : "BN",
        INVITATION : "I",
        INCOMING : "IN",
        OPTION : "O",
        MESSAGE : "M",
        SIPC_4_0 : "SIP-C/4.0",
        ACKNOWLEDGE : "A",
        # UNKNOW : "UNKNOW",
    }

SIP_HEADERS_PATTERN = '(?P<key>[A-Z]{1,2}): (?P<val>[a-zA-Z0-9@ :;".,\-=]*)'
SIP_HEADERS_RE_OBJ = re.compile(SIP_HEADERS_PATTERN, re.M)

def parse_sip_headers(buf):
    return SIP_HEADERS_RE_OBJ.findall(buf)
    
class SIPHeaders:
    def __init__(self, msg = None, headers = None):
        self.msg = msg
        self.headers = {}

        if headers:
            self.headers = headers

        if self.msg is not None:
            self._parse_msg(self.msg)

        if self.headers is not None:
            self._parse_headers(self.headers)

    def _parse_msg(self, msg):
        if msg.find(CRLF * 2) != STR_NOT_FOUND:
            headers = msg.split(CRLF * 2)[0]
        else:
            # `CRLF * 2` not found if msg get from response of standard httplib.HTTPConnection()
            headers = msg

        key_val_list = parse_sip_headers(headers)

        for key_val in key_val_list:
            self.add_header(key_val[0], key_val[1])

    def _parse_headers(self, headers):
        self.headers.update(headers)

    def __str__(self):
        buf = None
        if self.headers:
            buf = ""
            for key, val in self.headers.iteritems():
                if isinstance(val, list):
                    for element in val:
                        buf += "%s: %s" % (key, element) + CRLF
                else:
                    buf += "%s: %s" % (key, val) + CRLF

        return buf

    def get_field_value(self, key):
        if self.headers is None:
            return None
        return self.headers.get(key, None)

    def add_header(self, key, val):
        if key not in self.headers:
            self.headers[key] = val
        else:
            if isinstance(self.headers[key], list):
                self.headers[key].append(val)
            else:
                old_val = self.headers[key]
                self.headers[key] = [old_val, val]


SIP_HEADER_FIRST_LINE_PATTERN_A = '^%s (?P<code>[0-6]{3}) (?P<reason>[a-zA-Z ]{2,})' % PROTOCOL
SIP_HEADER_FIRST_LINE_RE_OBJ_A = re.compile(SIP_HEADER_FIRST_LINE_PATTERN_A)

SIP_HEADER_FIRST_LINE_PATTERN_B = '^(?P<method>[A-Z]{1,3}) (%s|[0-9]{9}) %s' % (HOME_DOMAIN, PROTOCOL)
SIP_HEADER_FIRST_LINE_RE_OBJ_B = re.compile(SIP_HEADER_FIRST_LINE_PATTERN_B)

def parse_sip_header_first_line(buf):
    if buf.startswith(PROTOCOL):
        results = SIP_HEADER_FIRST_LINE_RE_OBJ_A.findall(buf)
    else:
        results = SIP_HEADER_FIRST_LINE_RE_OBJ_B.findall(buf)
        
    if results:
        return results[0]

class SIPRequestHeaders(SIPHeaders):
    def __init__(self, sip_type = None, home_domain = None, protocol = None,
                 headers = None, first_line = None):
        SIPHeaders.__init__(self, headers = headers)

        self.sip_type = sip_type
        self.home_domain = home_domain
        self.protocol = protocol
        self.first_line = first_line

    def __str__(self):
        buf = SIPHeaders.__str__(self)

        if self.first_line is not None:
            return self.first_line + CRLF + buf
        else:
            first_line = "%s %s %s" % (str(self.sip_type), self.home_domain, self.protocol)
            return first_line + CRLF + buf


class SIPResponseHeaders(SIPHeaders):
    def __init__(self, msg, ignore_first_line):
        SIPHeaders.__init__(self, msg = msg)

        self.code = None
        self.body_length = None
        self.first_line = None
        self.ignore_first_line = ignore_first_line

        if msg:
            self.first_line = msg.split(CRLF)[0]
            self.code = self._get_code()
            self.body_length = self._get_body_length()

    def _get_body_length(self):
        if "L" in self.headers:
            return int(self.headers["L"])
        return None

    def _get_code(self):
        result = parse_sip_header_first_line(self.first_line)
        if result:
            code, reason = result[0], result[1]
            # something looks like `PROTOCOL 200 OK` or `R HOME_DOMAIN PROTOCOL'
            NOT_A_METHOD = len(code) == 3 and code[-1] < '7' and code[-1] > '-1'
            if NOT_A_METHOD:
                assert reason != None
                return int(code)

class SIPResponse():
    UNKNOW = -1
    OK = 200
    SEND_SMS_OK = 280
    UNAUTHORIED = 401

    EXTENSION_REQUIRED = 421 # login location changed, need verify
    CALL_TRANSACTION_DOES_NOT_EXIST = 481

    def __init__(self, all, ignore_first_line = False):
        self.all = all

        self.headers = SIPResponseHeaders(self.get_headers(self.all), ignore_first_line)
        self.code = self.headers.code
        self.body = self._get_body()

    @staticmethod
    def get_headers(res):
        return res.split(CRLF * 2)[0]

    def _get_body(self):
        res = self.all

        body_length = self.headers.get_field_value("L")
        if body_length is None:
            return ""
        else:
            body_length = int(body_length)

        headers_end = res.find(CRLF * 2)

        start = headers_end + len(CRLF * 2)
        end = headers_end + len(CRLF * 2) + body_length
        body = res[start:end]

        return body

    @staticmethod
    def get_body_length_from_msg(msg):
        siph_obj = SIPHeaders(msg = msg)
        return siph_obj.get_field_value("L")

    def get_sip_method(self):
        # add try for test new code, rm `try` in future
        try:
            result = parse_sip_header_first_line(self.headers.first_line)
        except AttributeError:
            logger.error(self.all)

        if result:
            method, home_domain_or_sid = result[0], result[1]
            assert home_domain_or_sid != None

            # something looks like `PROTOCOL 200 OK` or `R HOME_DOMAIN PROTOCOL'
            NOT_IS_A_METHOD = len(method) == 3 and method[-1] < '7' and method[-1] > '-1'
            if NOT_IS_A_METHOD:
                sip_method_const = SIP.get_const_by_str(SIP, PROTOCOL)
            else:
                sip_method_const = SIP.get_const_by_str(SIP, method)
            return sip_method_const

#    def get_sip_type(self):
#        t = self.headers.first_line
#
#        if t.startswith("I "):
#            return SIP.INVITATION
#        elif t.startswith("M "):
#            return SIP.MESSAGE
#        elif t.startswith("BN "):
#            return SIP.NOTIFICATION
#        elif t.startswith("SIP-C/4.0 "):# or t.startswith("SIP-C/2.0 "):
#            # some request's response, such as `set presence`
#            # response: `SIP-C/4.0 200 OK`
#            return SIP.SIPC_4_0
#        elif t.startswith("IN "):
#            return SIP.INCOMING # notify user are typing
#        elif t.startswith("O "):
#            return SIP.OPTION
#
#        raise Exception("get unknow sip type: %s" % repr(t))
#
#        return SIP.UNKNOWN

def sock_recv_debug_msg_filter(sock, buf, debug):
    res_obj = SIPResponse(buf)
    ip, port = sock.getpeername()

    sip_type = res_obj.get_sip_method()
    attr = res_obj.headers.get_field_value
    q_val = attr("Q")
    x_val = attr("X")
    l_val = attr("L")

    IS_KEEP_ALIVE_ACK = q_val == "2 R" and x_val == "600" and l_val == "481"
    IS_KEEP_CONN_BUSY = q_val == "1 O" and sip_type == SIP.SIPC_4_0
    prefix = "%s:%d recv:" % (ip, port)

    if IS_KEEP_ALIVE_ACK:
        msg = "%s %s" % (prefix, "a keep alive ack")
    elif IS_KEEP_CONN_BUSY:
        msg = "%s %s" % (prefix, "a keep connection busy ack")
    else:
        msg = "%s\n%s" % (prefix, buf)
        
    if debug:
        logger.debug(msg)


def sock_send_debug_msg_filter(sock, buf, debug):
    res_obj = SIPResponse(buf)
    ip, port = sock.getpeername()

    attr = res_obj.headers.get_field_value
    q_val = attr("Q")
    x_val = attr("X")
    l_val = attr("L")

    IS_KEEP_ALIVE_ACK = q_val == "2 R" and x_val == "600" and l_val == "481"
    prefix = "%s:%d send:" % (ip, port)

    if IS_KEEP_ALIVE_ACK:
        msg = "%s %s" % (prefix, "a {keep alive,keep connection busy}")
    else:
        msg = "%s\n%s" % (prefix, buf)

    if debug:
        logger.debug(msg)


class SIPConnection:
    def __init__(self, sock,
                 sip_type = None, headers = None, body = None,
                 home_domain = HOME_DOMAIN, protocol = PROTOCOL,
                 first_line = None):
        self.sock = sock
        self.headers = SIPRequestHeaders(sip_type = sip_type, home_domain = home_domain,
                                         protocol = protocol,
                                         headers = headers, first_line = first_line)
        self.body = to_byte_str(body)

    def generate_req(self):
        if self.body:
            self.headers.add_header("L", len(self.body))

        buf = str(self.headers)

        if self.body:
            buf += CRLF + self.body
        else:
            buf += CRLF

        return buf

    def send(self, size_once = SOCK_RECV_SIZE_ONCE, recv = True, debug = False):
        req = self.generate_req()

#        if debug:
#            logger.debug("-" * 60)
#            print self.sock.getpeername()
#            print "send: "
#            print req
        sock_send_debug_msg_filter(self.sock, req, debug)

        self.sock.send(req)

        if recv:
            buf = self.recv(self.sock, size_once = size_once, debug = debug)
            res_obj = SIPResponse(buf)
            return res_obj

    @staticmethod
    def recv(sock, size_once = SOCK_RECV_SIZE_ONCE, flags = None, debug = False):
        all_buf = ""

        while True:
            if flags is None:
                tmp = sock.recv(size_once)
            else:
                tmp = sock.recv(size_once, flags)

            if not tmp:
                break
            elif tmp.find(CRLF * 2) != STR_NOT_FOUND:
                all_buf += tmp
                break
            else:
                all_buf += tmp

        body_length = SIPResponse.get_body_length_from_msg(all_buf) or 0
        body_length = int(body_length)

        if body_length > 0:
            headers_buf = SIPResponse.get_headers(all_buf)
            recevied_body_length = len(all_buf) - (len(headers_buf) + len(CRLF * 2))

            while recevied_body_length < body_length:
                remain = body_length - recevied_body_length

                if flags is None:
                    tmp_buf = sock.recv(remain)
                else:
                    tmp_buf = sock.recv(remain, flags)

                all_buf += tmp_buf
                recevied_body_length += len(tmp_buf)

        sock_recv_debug_msg_filter(sock, all_buf, debug)

        return all_buf
    

def get_conversation_events(res_obj):
    try:
        body_dom = minidom.parseString(res_obj.body)
    except:
        traceback.print_exc(file = sys.stderr)

        print "res_obj.body:", res_obj.body

    event_nods = body_dom.getElementsByTagName("event")

    events = []

    for event_node in event_nods:
        type_attr = event_node.getAttribute("type")
        noti_event_type = NotificationEvent.get_const_by_str(NotificationEvent, type_attr)
        if noti_event_type is None:
            # unknow noti event
            continue
        events.append(int(noti_event_type))

    return events

def detect_user_if_is_offline_from_invite_response(res_obj):
    sip_type = res_obj.get_sip_method()

    sip_event = res_obj.headers.get_field_value("N")
    sip_event_const = SIPEvent.get_const_by_str(SIPEvent, sip_event)

    if sip_type == SIP.NOTIFICATION:
        events = get_conversation_events(res_obj)
        body_dom = minidom.parseString(res_obj.body)

        if sip_event_const == SIPEvent.CONVERSATION and NotificationEvent.USER_FAILED in events:
            member_node = body_dom.getElementsByTagName("member")[0]
            attr = member_node.getAttribute
            status = int(attr("status"))
            if status == httplib.BAD_GATEWAY:
                return True
    return False

def get_sid_from_uri(uri):
    if uri.find("sip:") != STR_NOT_FOUND:
        return strip2(uri, "sip:", "@")
    elif uri.find("tel:") != STR_NOT_FOUND:
        return strip2(uri, "tel:")


def i_send_keep_alive(user, debug = False):
    from_sid = user.sid
    call_id = str(user.get_global_call_id())
    sip_type = SIP(SIP.REGISTER)
    sip_event = SIPEvent(SIPEvent.KEEP_ALIVE)

    headers = {
        "F" : from_sid,
        "I" : call_id,
        "Q" : "%d %s" % (DEFAULT_SIP_SEQUENCE, str(sip_type)),

        "N" : str(sip_event)
        }
    body = '<args><credentials domains="%s" /></args>' % HOME_DOMAIN

    sip_conn = SIPConnection(user.get_sock(), sip_type = sip_type, headers = headers, body = body)
    sip_conn.send(debug = debug, recv = False)

def i_process_sipc_request_response(user, res_obj):
    if res_obj.body:
        body_dom = minidom.parseString(res_obj.body)

        # is SIP.SERVICE - SIPEvent.SET_PRESENCE response
        if res_obj.code == SIPResponse.OK and body_dom.getElementsByTagName("presence"):
            presence = body_dom.getElementsByTagName("basic")[0].getAttribute("value")
            user.set_presence(int(presence))
    else:
        q_val = res_obj.headers.get_field_value("Q")
        auth = res_obj.headers.get_field_value("A")
        call_id = res_obj.headers.get_field_value("I")

        # is SIP.REGISTER - SIPEvent.START_CHAT response
        if q_val == "2 S" and auth and auth.startswith("CS address="):
            conversations = user.get_conversations()
            for conv in conversations.values():
                if conv.call_id == call_id:
                    conv.start_chat_response = res_obj
                    return

def i_send_ack(res_obj, sock):
    attr = res_obj.headers.get_field_value

    from_uri = attr("F")
    call_id = attr("I")
    q_val = attr("Q")

    first_line = "SIP-C/4.0 200 OK"
    headers = {
        "F" : from_uri,
        "I" : call_id,
        "Q" : q_val
    }

    sip_conn = SIPConnection(sock, headers = headers, first_line = first_line)
    sip_conn.send(recv = False, debug = True)

def i_set_presence(user, presence, debug = False):
    from_sid = user.sid

    call_id = str(user.get_global_call_id())

    sip_type = SIP(SIP.SERVICE)
    sip_event = SIPEvent(SIPEvent.SET_PRESENCE)

    headers = {
        "F" : from_sid,
        "I" : call_id,
        "Q" : "%d %s" % (DEFAULT_SIP_SEQUENCE, str(sip_type)),
        "N" : str(sip_event),
        }

    body = '<args><presence><basic value="%s"/></presence></args>' % str(presence)
    sip_conn = SIPConnection(user.get_sock(), sip_type = sip_type, headers = headers, body = body)
    sip_conn.send(recv = False, debug = debug)


class SIPResponseValidity:
    NOT_COMPLETE = -1
    NO_LEN_BUT_COMPLETE = 0
    COMPLETE = 1
    

def is_a_complete_response(buf):
    res_obj = SIPResponse(buf)
    length = res_obj.headers.get_field_value("L")
    res = SIPResponseValidity.NOT_COMPLETE
    if length is None:
        if buf.find(CRLF * 2) != STR_NOT_FOUND:
            res = SIPResponseValidity.NO_LEN_BUT_COMPLETE
        else:
            res = SIPResponseValidity.NOT_COMPLETE
    elif length is not None and int(length) == len(res_obj.body):
        res = SIPResponseValidity.COMPLETE

    return res


def is_a_over_complete_response(buf):
    res_obj = SIPResponse(buf)
    all = res_obj.headers.msg + CRLF * 2 + res_obj.body
    return len(buf) != len(all)

def get_package_right_size(res_obj):
    all = res_obj.headers.msg + CRLF * 2 + res_obj.body
    return len(all)

def split_package(buf):
    pkgs = []
    last_recv = ""
    if not is_a_over_complete_response(buf):
        right_package = SIPResponse(buf)
        pkgs.append(right_package)
    else:
        while is_a_over_complete_response(buf):
            right_package = SIPResponse(buf)
            pkgs.append(right_package)
            remain = buf[get_package_right_size(right_package):]
            buf = remain
            res = is_a_complete_response(buf)
            if res == SIPResponseValidity.NOT_COMPLETE:
                last_recv = buf
                break
            else:
                right_package = SIPResponse(buf)
                pkgs.append(right_package)
    return pkgs, last_recv