#coding:utf-8
import binascii
import ctypes
import ctypes.util
import hashlib
import struct
import socket
from xml.dom import minidom

from libblah.consts import DEFAULT_GID, STRANGER_GROUP_GID, BLACKLIST_GROUP_GID, DEFAULT_SIP_SEQUENCE, \
    PROTOCOL_VERSION
from libblah.contact import Group, GroupAgent, Contact
from libblah.log import logger
from libblah.rsa import rsa
from libblah.sip import SIP, SIPConnection, get_sid_from_uri
from libblah.store import save_data_to_local_json
from libblah.strutils import to_unicode_obj, strip2
from libblah.utils import map_node_attr_to_obj, xml_node_attributes2dict


def _generate_sipc_auth_response(user, res_obj):
    digest = res_obj.headers.get_field_value("W")
#    print "digest:", digest
    nonce = strip2(digest, 'nonce="', '"')
    key = strip2(digest, 'key="', '"')
    user_id = user.user_id

    p1 = user.get_hashed_passwd()
#    print "p1:", p1
    aes_key = "e146a9e31efb41f2d7ab58ba7ccd1f2958ec944a5cffdc514873986923c64567"
    p2 = hashlib.sha1(struct.pack("i", int(user_id)) + binascii.a2b_hex(p1)).hexdigest()
    plain = nonce + binascii.a2b_hex(p2) + binascii.a2b_hex(aes_key)

    rsa_n = key[:-6]
    rsa_e = key[-6:]

    response = binascii.b2a_hex(rsa(plain, rsa_e, rsa_n[:256], False))
    assert len(response) == 256
    return response


_SIPC_AUTH_BODY_TPL = '''<args>
    <device machine-code="001676C0E351"/>
    <caps value="1ff"/><events value="7f"/>
    <user-info mobile-no="%s" user-id="%s">
        <personal version="%s" attributes="v4default"/>
        <custom-config version="%s"/>
        <contact-list version="%s"
            buddy-attributes="v4default"/>
    </user-info>
    <credentials domains="fetion.com.cn"/>
    <presence>
        <basic value="%d" desc=""/>
    </presence>
</args>'''


def _generate_sipc_auth_body(user):
    d = (user.mobile_no, user.user_id,
         user.version or "", user.custom_config_version or "",
         user.contact_list_version or "", int(user.get_presence()))

    return _SIPC_AUTH_BODY_TPL % d

def _parse_configs_node(user, user_info_node):
    pass

def _parse_services_node(user, user_info_node):
    pass

def _parse_quotas_node(user, user_info_node):
    pass

def _parse_custom_config_node(user, body_dom):
    custom_config_node = body_dom.getElementsByTagName("custom-config")[0]
    custom_config_version = custom_config_node.getAttribute("version")

    if user.custom_config_version == custom_config_version:
        logger.info("custom_config_version matched, skip update")
        return

    custon_config = custom_config_node.childNodes[0].data
    data = {"data" : custon_config, "sid" : user.sid}
    save_data_to_local_json(data, "custom_config.json")

def _parse_personal_node(user, body_dom):
    # results -> user-info -> personal
    personal_node = body_dom.getElementsByTagName("personal")[0]

    pn_attr = personal_node.getAttribute
    version = pn_attr("version")
    if user.version == version:
        logger.info("version matched, skip update")
        return

    map_node_attr_to_obj(personal_node, user)

    data = xml_node_attributes2dict(personal_node)
    data["sid"] = user.sid
    save_data_to_local_json(data, "personal_node.json")


def _parse_buddy_lists_node(contact_list_node):
    ga = GroupAgent()

    un_group = Group(gid = DEFAULT_GID, gname = to_unicode_obj("未分组"))
    ga.add_group(un_group)
    buddy_lists = contact_list_node.getElementsByTagName("buddy-lists")[0]
    for i in buddy_lists.childNodes:
        if i.nodeType == minidom.Node.TEXT_NODE:
            continue
        gid, gname = int(i.getAttribute("id")), i.getAttribute("name")
        group = Group(gid, gname)
        ga.add_group(group)

    stranger_group = Group(gid = STRANGER_GROUP_GID, gname = to_unicode_obj("陌生人"))
    ga.add_group(stranger_group)

    blacklist_group = Group(gid = BLACKLIST_GROUP_GID, gname = to_unicode_obj("黑名单"))
    ga.add_group(blacklist_group)

    return ga

def _create_contact_from_buddy_xml_node(user, node):
    # Notice: a buddy could belongs to two groups
    attr = node.getAttribute

    contact = Contact(user = user)
    contact.uri = attr("u")
    contact.sid = get_sid_from_uri(contact.uri)
    contact.user_id = attr("i")
    contact.nickname = to_unicode_obj(attr("n"))
    contact.relation_status = int(attr("r"))

    buddy_list_id = attr("l")
    if buddy_list_id:
        gids = [gid for gid in buddy_list_id.split(";") if gid.strip() and int(gid) >= DEFAULT_GID]
        if len(gids) != 1:
            logger.error("!!! User (SID: %s) has multiple GID" % contact.sid)
            print "gids:", gids
        gid = int(gids[0])
    else:
        gid = DEFAULT_GID
    contact.set_gid(gid)

    contact.portrait_crc = 0

    return contact

def _parse_buddies_node(user, parent):
    buddies_node = parent.getElementsByTagName("buddies")[0]

    for i in buddies_node.childNodes:
        if i.nodeType == minidom.Node.TEXT_NODE:
            continue

        contact = _create_contact_from_buddy_xml_node(user, i)
        #logger.info("contact info, URI: %s, GID: %d" % (contact.uri, contact.gid))
        user.group_agent.add_contact(contact)

def _parse_chat_friends_node(user, contact_list_node):
    # strangers group list
    chat_friends_node = contact_list_node.getElementsByTagName("chat-friends")[0]

    for cat_node in chat_friends_node.childNodes:
        if cat_node.nodeType == minidom.Node.TEXT_NODE:
            continue

        contact = Contact(user)
        contact.set_gid(STRANGER_GROUP_GID)
        attr = cat_node.getAttribute
        contact.uri = attr("u")
        contact.sid = get_sid_from_uri(contact.uri)
        contact.user_id = attr("i")
        user.group_agent.add_contact(contact)

def _parse_blacklist_node(user, contact_list_node):
    blacklist_node = contact_list_node.getElementsByTagName("blacklist")[0]

    for cat_node in blacklist_node.childNodes:
        if cat_node.nodeType == minidom.Node.TEXT_NODE:
            continue

        contact = Contact(user)
        contact.set_gid(BLACKLIST_GROUP_GID)
        attr = cat_node.getAttribute
        contact.uri = attr("u")
        contact.sid = get_sid_from_uri(contact.uri)
        contact.user_id = attr("i")
        user.group_agent.add_contact(contact)

def _parse_contact_list_node(user, body_dom):
    """ Should it add myself to contact_list:
        user.contact_list.append(user.to_contact()).
    """
    contact_list_node = body_dom.getElementsByTagName("contact-list")[0]
    contact_list_version = contact_list_node.getAttribute("version")
    if user.contact_list_version == contact_list_version:
        logger.info("contact_list_version matched, skip update")
        return

    # Notice: in libblah, `buddy_lists` means `buddy group lists`
    user.group_agent = _parse_buddy_lists_node(contact_list_node)

    _parse_buddies_node(user, contact_list_node)
    _parse_chat_friends_node(user, contact_list_node)
    _parse_blacklist_node(user, contact_list_node)

    save_contact_list_to_local(user)

def save_contact_list_to_local(user):
    groups_d = {}
    for group in user.group_agent.group_list:
        gid = int(group.gid)
        groups_d[gid] = group.gname

        contacts_d = {}
        for contact in group.contact_list:
            cat_d = contact.to_dict()
            sid = int(cat_d["sid"])
            contacts_d[sid] = cat_d
        data = {
            "contacts" : contacts_d,
            "sid" : user.sid
        }
        save_data_to_local_json(data, "%s_list.json" % group.gname)

    data = {"groups" : groups_d, "sid" : int(user.sid)}
    save_data_to_local_json(data, "group_list.json")

def i_update_user_after_sipc_auth_success(user, res_obj):
    """ get and set contacts, configurations, last login {time,ip} """
    body_dom = minidom.parseString(res_obj.body)

    # parse client node
    client_node = body_dom.getElementsByTagName("client")[0]
    map_node_attr_to_obj(client_node, user)

    # parse user-info node
    user_info_node = body_dom.getElementsByTagName("user-info")[0]
    _parse_personal_node(user, user_info_node)
    _parse_configs_node(user, user_info_node)
    _parse_custom_config_node(user, user_info_node)
    _parse_contact_list_node(user, user_info_node)
    # ignore score node
    _parse_services_node(user, user_info_node)
    _parse_quotas_node(user, user_info_node)
    # ignore capability-list node

    #user.contact_list.append(user.to_contact())

    data = {
        "version" : user.version,
        "contact_list_version" : user.contact_list_version,
        "custom_config_version" : user.custom_config_version,
        "sid" : user.sid,
        }
    save_data_to_local_json(data, "user_info_versions.json")


#def save_personal_to_local(personal_node):
#    d = xml_node_attributes2dict(personal_node)
#    save_data_to_local_json(d, "personal_config.json")

def _rand():
    ''' From man: return a sequence of pseudo-random integers in the range of 0 to RAND_MAX
    on Mac OS X 10.6, RAND_MAX is equal to  0x7fffffff  '''

    path = ctypes.util.find_library('c')
    clib = ctypes.cdll.LoadLibrary(path)
    return clib.rand()

def _generate_cnouce():
    cnouce = "%04X%04X%04X%04X%04X%04X%04X%04X" % (
        _rand() & 0xFFFF, _rand() & 0xFFFF,
        _rand() & 0xFFFF, _rand() & 0xFFFF,
        _rand() & 0xFFFF, _rand() & 0xFFFF,
        _rand() & 0xFFFF, _rand() & 0xFFFF)
    return cnouce
    
def i_sipc_auth(user, verification = None, debug = False):
    # register to SIPC server
    config = user.get_config()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    user.set_sock(sock)
    splits = config.sipc_proxy.split(":")
    ip, port = splits[0], splits[1]
    sock.connect((ip, int(port)))
#    SIPC_PROXY_IP = '58.68.229.64'
#    SIPC_PROXY_PORT = 8080
#    sock.connect((SIPC_PROXY_IP, SIPC_PROXY_PORT))

    from_sid = user.sid
    call_id = user.get_global_call_id()
    sip_type = SIP(SIP.REGISTER)

    headers = dict({
        "F" : from_sid,
        "I" : str(call_id),
        "Q" : "%d %s" % (DEFAULT_SIP_SEQUENCE, str(sip_type)),

        "CN" : _generate_cnouce(),
        "CL" : 'type="PC" ,version="%s"' % PROTOCOL_VERSION
        })

    sip_conn = SIPConnection(sock, sip_type = sip_type, headers = headers)
    res_obj = sip_conn.send(debug = debug)


    call_id = user.get_global_call_id()
    sip_type = SIP(SIP.REGISTER)

    response = _generate_sipc_auth_response(user, res_obj)

    headers = dict({
        "F" : from_sid,
        "I" : str(call_id),
        "Q" : "%d %s" % (DEFAULT_SIP_SEQUENCE, str(sip_type)),

        "AK" : "ak-value",
        "A" : 'Digest response="%s",algorithm="SHA1-sess-v4"' % response,
        })

    # append verification created in SSI auth
    if verification:
        auth = 'Verify response="%s",algorithm="%s",type="%s",chid="%s"' % \
            (verification.chars, verification.algorithm, verification._type, verification.pid)
        old_val = headers["A"]
        headers["A"] = [old_val, auth]

    body = _generate_sipc_auth_body(user)

    sip_conn = SIPConnection(user.get_sock(), sip_type = sip_type, headers = headers, body = body)
    res_obj = sip_conn.send(debug = debug)

    return res_obj
