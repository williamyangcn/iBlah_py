import errno
import httplib
import os
import urllib
import urlparse
import socket
import time
from libblah.consts import YES
from libblah.log import logger

from libblah.sip import get_sid_from_uri
from libblah.http import HTTPResponse


def i_download_portrait_by_uri(user, uri, debug = False):
    params = {
        "Uri" : uri,
        "Size" : 120,
        "c" : user.get_ssi_cookie(),
    }
    config = user.get_config()

    parses = urlparse.urlparse(config.get_uri)
    root_path = [i for i in parses.path.split('/') if i][0]
    path = "/%s/getportrait.aspx" % root_path
    query = urllib.urlencode(params)
    url = "%s?%s" % (path, query)
    
    headers = {
        "Accept" : config.portrait_file_type,
        }

    httplib.HTTPConnection.response_class = HTTPResponse
    conn = httplib.HTTPConnection(parses.netloc)

#    if debug:
#        debuglevel = 1
#    else:
#        debuglevel = 0
#    conn.set_debuglevel(debuglevel)

    conn.request("GET", url, headers = headers)
    res_obj = conn.getresponse()
    conn.close()

    if debug:
        logger.info("request")
        print "url", url
        from pprint import pprint as pp
        print "headers:", pp(headers)

    if debug:
        logger.info("response")
        print "code:", res_obj.code
        print "msg:", res_obj.msg

    if res_obj.code == httplib.OK:
        sid = get_sid_from_uri(uri)
        ct = res_obj.headers.get_field_value('Content-Type')
        format_suffix = ct.split('/')[-1].lower()
        #format_suffix = "jpg"
        portrait_save_path = os.path.join(user.get_portrait_save_path(), "%s.%s" % (sid, format_suffix))
        with open(portrait_save_path, "wb") as f:
            f.write(res_obj.body)

    return res_obj

def i_update_all_portraits(user, debug = False):
    all_contacts = user.group_agent.get_all_contacts()
    for contact in all_contacts:
        if (not contact.get_portrait_path()) or (contact.image_changed == YES):
            # server will active close socket and client get errno.ECONNRESET
            # if download too fast
            #i_download_portrait_by_uri(user, contact.uri, debug = debug)
            try:
                i_download_portrait_by_uri(user, contact.uri, debug = debug)
            except socket.error as (err_no, err_msg):
                if err_no == errno.ECONNRESET:
                    time.sleep(0.5)
