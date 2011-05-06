import httplib
from libblah.consts import CRLF, STR_NOT_FOUND


class HTTPHeaders:
    SEPARATOR = ": "
    def __init__(self, msg = None, headers = None):
        self._msg = ""
        self._headers = {}

        if msg:
            if msg.find(CRLF * 2) != STR_NOT_FOUND:
                msg = msg.split(CRLF)[0]
            self._msg = msg
            self._parse_msg()

        if headers:
            self._headers = headers
            self._parse_headers(self._headers)

    def __str__(self):
        buf = None
        if self._headers:
            buf = ""
            for key, val in self._headers.iteritems():
                buf += "%s: %s" % (key, val) + CRLF

        return buf

    def _parse_msg(self):
        key_val_list = [i for i in self._msg.split(CRLF) if i.strip()]
        for key_val in key_val_list:
            splits = key_val.split(self.SEPARATOR)
            key, val = splits[0], splits[1]
            self._add_header(key, val)

    def get_field_value(self, key):
        if self._headers is None:
            return None
        return self._headers.get(key, None)

    def _add_header(self, key, val):
        assert key not in self._headers
        self._headers[key] = val

    def _parse_headers(self, headers):
       self._headers.update(headers)


class HTTPResponse(httplib.HTTPResponse):
    NETWORK_DISABLE = -1
    PASSWD_ERROR = 401
    CCPS_CHECK_ERROR = 420 # verification invalid
    NEED_VERIFY = 421
    def __init__(self, sock, debuglevel =  0, strict = 0, method = None,
                 read_body = True):
        httplib.HTTPResponse.__init__(self, sock, debuglevel, strict, method)

        self.headers = None

        if read_body:
            self.begin()
            self.body = self.read()

            self.headers = HTTPHeaders(msg = str(self.msg))
        else:
            self.body = None

            self.headers = HTTPHeaders(msg = str(self.msg))

        if debuglevel != 0:
            print "body:", self.body

        self.code = self.status
