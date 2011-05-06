#coding:utf-8
import base64
import httplib
import os
from xml.dom import minidom
from libblah.consts import get_user_config_path, PROTOCOL_VERSION
from libblah.strutils import strip2
from libblah.http import HTTPResponse


class Verification:
    def __init__(self, algorithm, _type, text, tips):
        self.algorithm = algorithm
        self._type = _type
        self.text = text
        self.tips = tips
        self.pid = None # Picture uuID

        self.chars = None # set use recognised 4 characters
        self.picture_path = None # JPEG format

"""
SIP-C/4.0 421 Extension Required
    I: 2
    Q: 2 R
    W: Verify algorithm="picc-ChangeMachine",type="GeneralPic"
    L: 176

    <results>
<reason text="您本次变更了登录地点。为保障您的帐号安全，请输入验证字符，这可以防止恶意程序的自动登录。" tips=""/>
</results>"""

def i_generate_verification_pic(user, res_obj, debug = False):
    """ There two types response, HTTP status 421 or SIPResponse code 421,
        the former response body contains verification node, the latter contains reason note only. """

    body_dom = minidom.parseString(res_obj.body)
    veri_nodes = body_dom.getElementsByTagName("verification")
    if veri_nodes:
        veri_node = veri_nodes[0]
        attr = veri_node.getAttribute

        algorithm = attr("algorithm")
        _type = attr("type")
        text = attr("text")
        tips = attr("tips")
    else:
        reason_node = body_dom.getElementsByTagName("reason")[0]
        w_val = res_obj.headers.get_field_value("W")

        algorithm = strip2(w_val, 'algorithm="', '",')
        _type = strip2(w_val, 'type="', '"')
        text = reason_node.getAttribute("text")
        tips = ""
    veri = Verification(algorithm = algorithm, _type = _type, text = text, tips = tips)

    ssi_cookie = user.get_ssi_cookie() or ""
    host = "nav.fetion.com.cn"

    headers = dict({
        'Cookie' : 'ssic=%s' % ssi_cookie,
        "Connection" : "close",
        "User-Agent" : "IIC2.0/PC %s" % PROTOCOL_VERSION,
        })

    httplib.HTTPConnection.response_class = HTTPResponse
    conn = httplib.HTTPConnection(host)

    if debug:
        debuglevel = 1
    else:
        debuglevel = 0
    conn.set_debuglevel(debuglevel)

    if veri.algorithm:
        algorithm = veri.algorithm
    else:
        algorithm = ""
    url = '/nav/GetPicCodeV4.aspx?algorithm=%s' % algorithm
    conn.request("GET", url, headers = headers)
    res_obj = conn.getresponse()

    assert httplib.OK == res_obj.status

    body_dom = minidom.parseString(res_obj.body)
    conn.close()

    pic_cert_node = body_dom.getElementsByTagName("pic-certificate")[0]
    attr = pic_cert_node.getAttribute
    veri.pid = attr("id")

    pic_base64 = attr("pic")
    pic_save_path = os.path.join(get_user_config_path(), "%s" % user.sid, "verify_code.jpeg")
    with open(pic_save_path, "wb") as f:
        f.write(base64.decodestring(pic_base64))
    veri.picture_path = pic_save_path

    return veri
