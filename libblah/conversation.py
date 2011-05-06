import time
from libblah.log import logger
from libblah.sip import SIP, SIPEvent, SIPConnection
from libiblah.qthread import kill_qthread


class Conversation:
    def __init__(self, to_uri):
        self.call_id = None
        self.to_uri = to_uri
        self.sock = None
        self.listen_thread = None

        self.send_msg_thread = None
        self.get_sock_for_recv_msg_thread = None
        self.keep_conn_busy_thread = None

        # create conversation sock from response ip, port
        self.start_chat_response = None

    def over(self):
        if self.keep_conn_busy_thread:
            logger.debug("cancel keep_conn_busy_thread ...")
            self.keep_conn_busy_thread.cancel()
            
        self.sock.close()

#        if self.listen_thread and not self.listen_thread.isFinished():
#            logger.debug("terminate listen_thread of conversation ...")
#            kill_qthread(self.listen_thread)
            

def i_keep_connection_busy(user, sock, debug = False):
    from_sid = user.sid
    sip_type = SIP(SIP.OPTION)
    sip_event = SIPEvent(SIPEvent.KEEP_CONNECTION_BUSY)

    call_id = str(user.get_global_call_id())

    headers = {
        "F" : from_sid,
        "I" : call_id,
        "Q" : "1 %s" % str(sip_type),
        "N" : str(sip_event),
    }

    sip_conn = SIPConnection(sock, sip_type = sip_type, headers = headers)
    sip_conn.send(recv = False, debug = debug)
