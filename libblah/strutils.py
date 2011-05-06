import sys

STR_NOT_FOUND = -1
SHUGE_DEFAULT_ENCODING = "utf-8"

# encoding handler
def to_unicode_obj(obj, is_filename = False):
    """ Convert byte string to unicode object.

    Arguments:
    - `is_filename`: set this True if `obj` is get from Microsoft Windows file
                  system, such as os.listdir. """

    if is_filename and sys.platform == "win32":
        file_sys_encoding = sys.getfilesystemencoding()
        return obj.decode(file_sys_encoding)

    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding = SHUGE_DEFAULT_ENCODING)
    return obj

def to_byte_str(obj):
    if isinstance(obj, basestring):
        if not isinstance(obj, str):
            obj = obj.encode(SHUGE_DEFAULT_ENCODING)
    return obj


def strip2(src, start_token, end_token=None):
    '''
    return str between start_token and end_token.

    >>> src = "blah=blahme;"
    >>> start_token = 'blah='
    >>> end_token = ';'
    >>> assert "blahme" == strip_str(src, start_token, end_token)
    '''
    pos = src.find(start_token)
    if pos == STR_NOT_FOUND:
        return None
    start = pos + len(start_token)
    tmp = src[start:]

    if end_token is not None:
        end = tmp.find(end_token)
        if end == STR_NOT_FOUND:
            return tmp
        return tmp[:end]
    return tmp
