import calendar
import datetime
import re
import time
from xml.dom import minidom
from libblah.strutils import to_unicode_obj


def qstr_to_unicode_obj(qstr):
    return to_unicode_obj(str(qstr.toUtf8()))


def get_now_datetime_str():
    """ Get local date and time """
    return str(datetime.datetime.now())[:19]

#ts_str = 'Sat, 05 Mar 2011 17:03:05 GMT'

def str_to_float(ts_str, format = "%a, %d %b %Y %H:%M:%S %Z", local = False):
    """ ack timestamp format:
    format = "%a, %d %b %Y %H:%M:%S %Z"
    """
    ts_struct = time.strptime(ts_str, format)
    if local:
        return time.mktime(ts_struct)
    return float(calendar.timegm(ts_struct))

#print str_to_float(ts_str)
#print str_to_float(ts_str, local = True)

def flaot_to_str(ts_str, format = "%a, %d %b %Y %H:%M:%S %Z", local = False):
    """ 'Sun, 06 Mar 2011 01:29:01 GMT'
        'Sat, 05 Mar 2011 17:29:01 CST'
    """
    if local:
        ts_struct = time.localtime(ts_float)
    else:
        ts_struct = time.gmtime(ts_float)
    return time.strftime(format, ts_struct)

#ts_float = 1299346141.0
#print flaot_to_str(ts_float)
#print flaot_to_str(ts_float, local = True)


SINGLE_LINE_PATTERN = "<(.*?)>"
s_prog = re.compile(SINGLE_LINE_PATTERN, re.I | re.U | re.M)

MULTI_LINES_PATTERN = "</(.*?)'>"
m_prog = re.compile(MULTI_LINES_PATTERN, re.I | re.U | re.M)

DOS_LINESEP_PATTERN = r'\r'
dos_prog = re.compile(DOS_LINESEP_PATTERN, re.M)

def rm_markups(txt):
    SINGLE_LINE_START_TOKEN = "<Font Face"

    if txt.startswith(SINGLE_LINE_START_TOKEN):
        clean = s_prog.sub("", txt)
    else:
        clean = m_prog.sub("<br />", txt)

    return dos_prog.sub("<br />", clean)


def map_node_attr_to_obj(node, obj, filters = None):
    """ TODO: add ignore_list paramters """
    attrs = node.attributes.keys()
    for i in attrs:
        key = i
        val = node.getAttribute(key)
        if filters and key in filters:
            key, val = filters[key](key, val)
        if hasattr(obj, key.replace('-', '_')):
            setattr(obj, key.replace('-', '_'), to_unicode_obj(val))


def xml_node_attributes2dict(node):
    """ structure: <root> <a name="foo" /> <b name="bar" /> </root>
        -->
        root = {
            "a" : "foo",
            "b" : "bar",
        }
    """
    items = node.attributes.items()
    items.sort()
    d = {}
    for item in items:
        key, val = item[0].replace("-", "_"), item[1]
        d[key] = val

    return d

def map_dict_to_obj(d, obj, filters = None):
    """ root = {
            "a" : "foo",
            "b" : "bar"
        }
        -->
        class XXOO:
            self.a = "foo"
            self.b = "bar"
    """
    for key, val in d.iteritems():
        if filters and key in filters:
            key, val = filters[key](key, val)
        #if key in obj.__dict__:
        setattr(obj, key, val)


def map_config_xml_to_obj(obj, body_dom, node_name_list, filters = None):
    """ structure: <root> <a>foo</a> <b>bar</b> </root>
        -->
        class XXOO:
            self.a = "foo"
            self.b = "bar"
    """
    for name in node_name_list:
        nodes = body_dom.getElementsByTagName(name)
        if not nodes:
            continue
        servers_node = nodes[0]
        for node in servers_node.childNodes:
            if node.nodeType == minidom.Node.TEXT_NODE:
                continue

            key = node.nodeName.replace("-", "_")

            # skip node which there is no child
            if not node.childNodes:
                continue

            # skip node which there are more than one child
            if len(node.childNodes) > 1:
                continue

            val = node.childNodes[0].data.strip("\n").strip("\t").strip("\n")
            if filters and key in filters:
                key, val = filters[key](key, val)
            #if key in obj.__dict__:
            setattr(obj, key, val)
