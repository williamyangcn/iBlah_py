import socket
import time
from libblah.consts import DEFAULT_SIP_SEQUENCE
from libblah.log import logger
from libblah.sip import SIPEvent, SIP, SIPConnection, SIPResponse, \
    detect_user_if_is_offline_from_invite_response
from libblah.strutils import strip2, to_byte_str


def start_chat(user, to_uri, debug = False):
    """ Get (ip, port) to create a socket which used to start a online conversation """
    from_sid = user.sid
    sip_type = SIP(SIP.SERVICE)
    sip_event = SIPEvent(SIPEvent.START_CHAT)

    call_id = str(user.get_global_call_id())

    headers = {
        "F" : from_sid,
        "I" : call_id,
        "Q" : "%d %s" % (DEFAULT_SIP_SEQUENCE, str(sip_type)),
        "N" : str(sip_event),
    }

    conversations = user.get_conversations()
    conversations[to_uri].call_id = call_id

    sip_conn = SIPConnection(user.get_sock(), sip_type = sip_type, headers = headers)
    sip_conn.send(recv = False, debug = debug)

def _get_ip_port_credential_from_auth_field(auth):
    splits = strip2(auth, 'CS ').split(',')
    ip = strip2(splits[0], 'address="', ':')
    port = int(strip2(splits[0], ":", ";"))
    credential = strip2(splits[1], 'credential="', '"')
    return ip, port, credential

def get_sock_for_send_msg(user, to_uri, debug = False):
    """ Parse (ip, port) get by start_chat request,
        create a new socket object to register and invite buddy to start a online conversation. """

    conversations = user.get_conversations()
    conv = conversations[to_uri]
    while not conv.start_chat_response:
        time.sleep(0.1)
    res_obj = conv.start_chat_response

    auth_val = res_obj.headers.get_field_value("A")
    ip, port, credential = _get_ip_port_credential_from_auth_field(auth_val)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conv.sock = sock
    sock.connect((ip, port))

    call_id = conv.call_id
    sip_type = SIP(SIP.REGISTER)
    sid = user.sid

    headers = {
        "F" : sid,
        "I" : call_id,
        "Q" : "%d %s" % (DEFAULT_SIP_SEQUENCE, str(sip_type)),

        "K" : ["text/html-fragment", "multiparty", "nudge"],
        "A" : 'TICKS auth="%s"' % credential,
    }

    conn = SIPConnection(sock, sip_type = sip_type, headers = headers)
    conn.send(debug = debug)

    # invite_buddy_to_start_chat(user, call_id, to_uri, debug)
    sip_type = SIP(SIP.SERVICE)
    sip_event = SIPEvent(SIPEvent.INVITE_BUDDY)

    headers = {
        "F" : sid,
        "I" : call_id,
        "Q" : "%d %s" % (DEFAULT_SIP_SEQUENCE, str(sip_type)),
        "N" : str(sip_event),
    }

    body = '<args><contacts><contact uri="%s" /></contacts></args>' % to_uri

    conn = SIPConnection(sock, sip_type = sip_type, headers = headers, body = body)
    res_obj = conn.send(debug = debug)

    if res_obj.code != SIPResponse.OK:
        sock.close()
        logger.error("get sock for cat failed")
        return None

    # recevie option response, we can do detect user if is offline or hide from response
    buf = SIPConnection.recv(sock, debug = debug)
    res_obj = SIPResponse(buf)
    
    logger.info("user is offline: %s" % str(detect_user_if_is_offline_from_invite_response(res_obj)))
    if detect_user_if_is_offline_from_invite_response(res_obj):
        sock.close()
        return None

    assert res_obj != None

    # recevie conversation response
    buf = SIPConnection.recv(sock, debug = debug)
    res_obj = SIPResponse(buf)
    assert res_obj != None

    return res_obj

def i_send_msg(user, to_uri, msg, debug = True):
    conversations = user.get_conversations()
    if to_uri in conversations:
        conv = conversations[to_uri]

        if conv.listen_thread and not conv.listen_thread.isFinished():
            sock = conv.sock
        else:
            start_chat(user, to_uri, debug = debug)
            res_obj = get_sock_for_send_msg(user, to_uri, debug = debug)
            if res_obj:
                sock = conv.sock
            else:
                conv = conversations[to_uri]
                conv.sock = user.get_sock()
                sock = conv.sock
    else:
        conv = conversations[to_uri]
        conv.sock = user.get_sock()
        sock = conv.sock

    call_id = str(user.get_global_call_id())

    from_sid = user.sid
    sip_type = SIP(SIP.MESSAGE)
    sip_event = SIPEvent(SIPEvent.CAT_MESSAGE)

    headers = {
        "F" : from_sid,
        "I" : call_id,
        "Q" : "%d %s" % (DEFAULT_SIP_SEQUENCE, str(sip_type)),

        "N" : str(sip_event),

        "T" : to_uri,
        "C" : "text/plain",
        "K" : "SaveHistory",
    }

    body = to_byte_str(msg)
    sip_conn = SIPConnection(sock, sip_type = sip_type, headers = headers, body = body)

    """TODO: we should add this msg into unack_msg_list,
        traversal un-ack message list in 20s interval,
        pop up a send message failed warning for no un-ack message. """

    unack_msg = {
        "send_ts" : int(time.time()),
        "call_id" : call_id,
        "to_uri" : to_uri,
        "content" : msg,
        }
    user.append_to_unack_msg_list(unack_msg)

    sip_conn.send(recv = False, debug = debug)

def get_sock_for_recv_msg(user, res_obj, debug = False):
    attr = res_obj.headers.get_field_value

    auth = attr("A")
    ip, port, credential = _get_ip_port_credential_from_auth_field(auth)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))

    from_sid = user.sid
    call_id = attr("I")

    sip_type = SIP(SIP.REGISTER)

    headers = {
        "F" : from_sid,
        "I" : call_id,
        "Q" : "1 %s" % str(sip_type),

        # "K" : kinds = attr("K")
        # `K` means `media kind` ?
        "K" : ["text/html-fragment", "multiparty", "nudge"],
        "A" : 'TICKS auth="%s"' % credential,
    }

    sip_conn = SIPConnection(sock, sip_type = sip_type, headers = headers)
    res_obj = sip_conn.send(debug = debug)


    if res_obj.code != SIPResponse.OK:
        logger.error("!!! get_sock_for_recv_msg failed")
    else:
        from_uri = attr("F")
        conversations = user.get_conversations()
        conv = conversations[from_uri]
        conv.call_id = call_id
        conv.sock = sock

    return res_obj


#def i_send_msg_to_mobile(user, receive_no, msg, debug = False):
#    ''' send msg to mobile by mobile NO. or fetion NO. '''
#    if receive_no.find("sip:") != STR_NOT_FOUND:
#        to_uri = receive_no
#    else:
#        if user.mobile_no == receive_no:
#            to_uri = user.uri
#        else:
#            to_uri = get_uri_by_mobile_no_or_sid(user, receive_no)
#
#    from_sid = user.sid
#    sock = user.sock
#    call_id = user.global_call_id
#    user.global_call_id += 1
#
#    sip_type = SIP(SIP.MESSAGE)
#    sip_event = SIPEvent(SIPEvent.SEND_CAT_MESSAGE)
#
#    headers = {
#        "F" : from_sid,
#        "I" : str(call_id),
#        "Q" : "%d %s" % (DEFAULT_SIP_SEQUENCE, str(sip_type)),
#
#        "N" : str(sip_event),
#        "T" : to_uri
#    }
#    body = msg
#
#    sip_conn = SIPConnection(sock, sip_type = sip_type, headers = headers, body = body)
#    res_obj = sip_conn.send(debug = debug)
#
#    logger.info('send SMS to mobile response code: %d' % res_obj.code)
#
#    return res_obj

#def get_uri_by_mobile_no_or_sid(user, no):
#    """ get URI by mobile NO. SID """
#    if len(no) == IS_MOBILE_NO:
#        mobile_no = no
#        target_cat = get_contact_by_account_no(user, mobile_no)
#        for cat in user.contact_list:
#            if target_cat.user_id == cat.user_id:
#                return cat.uri
#    elif len(no) == IS_SID:
#        sid = no
#        for cat in user.contact_list:
#            if cat.sid == sid:
#                return cat.uri
#
#    return None

#GET_CAT_BODY_TPL = '<args><contact uri="%s" /></args>'
#
#def get_contact_by_account_no(user, no):
#    """ get contact info by SID or mobile NO. """
#    sock = user.sock
#
#    from_sid = user.sid
#    call_id = user.global_call_id
#    user.global_call_id += 1
#    sip_type = SIP(SIP.SERVICE)
#    sip_event = SIPEvent(SIPEvent.GET_CONTACT_INFO)
#
#    headers = {
#        "F" : from_sid,
#        "I" : str(call_id),
#        "Q" : "%d %s" % (DEFAULT_SIP_SEQUENCE, str(sip_type)),
#        "N" : str(sip_event)
#    }
#
#    uri = None
#    if len(no) == IS_MOBILE_NO:
#        uri = "tel:" + no
#    elif len(no) == IS_SID:
#        uri = "sip:" + no
#    body = GET_CAT_BODY_TPL % uri
#
#    sip_type = SIP(SIP.SERVICE)
#
#    sip_conn = SIPConnection(sock, sip_type = sip_type, headers = headers, body = body)
#    res_obj = sip_conn.send(debug = True)
#
#    if res_obj.code == SIPResponse.OK:
#        body_dom = minidom.parseString(res_obj.body)
#        cat_node = body_dom.getElementsByTagName("contact")[0]
#        cat = Contact(user = user)
#        map_node_attr_to_obj(cat_node, cat)
#        return cat
#
#    return None
