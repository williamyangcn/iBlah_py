#coding:utf-8
import errno
import os
from xml.dom import minidom
import select
import socket
import time
from functools import wraps
import threading

from PyQt4 import QtGui
from PyQt4 import QtCore
from ui.ui_contact_list import Ui_ContactListWindow
from libblah.consts import SERVICE_PROVIDER_URI, NO, YES, UserPresence
from libblah.conversation import Conversation, i_keep_connection_busy
from libblah.log import logger
from libblah.portrait import i_download_portrait_by_uri
from libblah.utils import map_node_attr_to_obj, rm_markups
from libblah.contact import Contact, ReplyAddBuddyApplication, \
    i_delete_buddy, i_reply_add_buddy, i_parse_add_buddy_refused, i_subscribe_contact_list, GroupAgentItemType, i_add_buddy, i_parse_add_buddy_application
from libblah.sip import SIPConnection, SIP, SIPResponse, SIPEvent, \
    i_process_sipc_request_response, i_send_keep_alive, i_send_ack, \
    get_conversation_events, get_sid_from_uri, i_set_presence, NotificationEvent, is_a_complete_response, SIPResponseValidity, split_package
from libblah.strutils import to_unicode_obj, STR_NOT_FOUND
from libblah.portrait import i_update_all_portraits
from libblah.message import get_sock_for_recv_msg
from libiblah.chat_win import OTHER_LOG_TPL, ChatWindow
from libiblah.popup_dlgs import popup_error, popup_about
from libiblah.profile_dlg import ProfileDialog
from libiblah.qthread import PeriodicExecutor, IThread
from libiblah.contact_crud import DeleteBuddyDialog, ReplyAddBuddyDialog, AddBuddyDialog
from libiblah.const import LOGO_PATH, DEFAULT_PORTRAIT_PATH


def portrait_left_click_wrapper(func, parent):
    @wraps(func)
    def wrapper(evt):
        #QtGui.QLabel.mousePressEvent(parent, evt)
        if evt.button() == QtCore.Qt.LeftButton:
            parent.emit(QtCore.SIGNAL('leftClicked()'))
        func(evt)
    return wrapper

def contact_list_view_left_click_wrapper(func, parent):
    @wraps(func)
    def wrapper(evt):
        parent.emit(QtCore.SIGNAL("leftClicked()"))
        func(evt)
    return wrapper

def contact_list_double_click_wrapper(func, parent):
    @wraps(func)
    def wrapper(evt):
        #QtGui.QTreeView.mouseDoubleClickEvent(parent, evt)
        parent.emit(QtCore.SIGNAL("doubleClicked()"))
        func(evt)
    return wrapper

def to_grayscaled(path):
    origin = QtGui.QPixmap(path)

    img = origin.toImage()
    for i in xrange(origin.width()):
        for j in xrange(origin.height()):
            col = img.pixel(i, j)
            gray = QtGui.qGray(col)
            img.setPixel(i, j, QtGui.qRgb(gray, gray, gray))

    dst = origin.fromImage(img)
    return dst


class ContactListTreeModel(QtCore.QAbstractItemModel):
    FIRST_COLUMN = 0
    COLUMN_COUNT = 1
    def __init__(self, group_agent):
        QtCore.QAbstractItemModel.__init__(self)
        self.group_agent = group_agent

        ofline_pixmap_widget = to_grayscaled(DEFAULT_PORTRAIT_PATH)
        width, height = 50, 50
        ofline_pixmap_widget = ofline_pixmap_widget.scaled(QtCore.QSize(width, height))

        online_pixmap_widget = to_grayscaled(DEFAULT_PORTRAIT_PATH)
        online_pixmap_widget = online_pixmap_widget.scaled(QtCore.QSize(width, height))

        URI_OFFLINE = UserPresence.OFFLINE_OR_INVISIBLE
        URI_ONLINE = UserPresence.ONLINE

        self._portrait_cache = {
            URI_OFFLINE : {
                "presence" : UserPresence.OFFLINE_OR_INVISIBLE,
                "pixmap_widget" : ofline_pixmap_widget,
            },
            URI_ONLINE : {
                "presence" : UserPresence.ONLINE,
                "pixmap_widget" : online_pixmap_widget,
            },
        }

    def get_portrait_by_uri(self, uri):
        if uri in self._portrait_cache:
            return self._portrait_cache[uri]["pixmap_widget"]

        contact = self.group_agent.get_contact_by_uri(uri)
        IS_SYS_MSG = contact is None

        if IS_SYS_MSG:
            pix_widget = self._portrait_cache[UserPresence.OFFLINE_OR_INVISIBLE]["pixmap_widget"]
        elif contact.presence > UserPresence.OFFLINE_OR_INVISIBLE:
            pix_widget = self._portrait_cache[UserPresence.ONLINE]["pixmap_widget"]
        else:
            pix_widget = self._portrait_cache[UserPresence.OFFLINE_OR_INVISIBLE]["pixmap_widget"]
        return pix_widget

    def columnCount(self, parent_idx):
        if not parent_idx.isValid():
            return self.COLUMN_COUNT

        parent_obj = parent_idx.internalPointer()
        return parent_obj.count()

    def rowCount(self, parent_idx):
        if not parent_idx.isValid():
            return self.group_agent.count()

        parent_obj = parent_idx.internalPointer()
        if parent_obj.get_type() == GroupAgentItemType.GROUP:
            return parent_obj.count()

        return 0

    def index(self, row, column, parent_idx):
        assert column != None
        if not parent_idx.isValid():
            group = self.group_agent.get_group_by_row(row)
            return self.createIndex(row, column, group)

        parent_obj = parent_idx.internalPointer()
        if parent_obj.get_type() == GroupAgentItemType.GROUP:
            item = parent_obj.get_contact_by_row(row)
            return self.createIndex(row, column, item)

        return QtCore.QModelIndex()

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()

        obj = index.internalPointer()
        obj_type = obj.get_type()
        if role == QtCore.Qt.DisplayRole:
            if obj_type in (GroupAgentItemType.GROUP, GroupAgentItemType.CONTACT):
                return QtCore.QVariant(obj.get_display_name())

        elif role == QtCore.Qt.UserRole:
            if obj_type == GroupAgentItemType.GROUP:
                return QtCore.QVariant(obj.gid)
            elif obj_type == GroupAgentItemType.CONTACT:
                return QtCore.QVariant(obj.uri)

        elif role == QtCore.Qt.ToolTipRole:
            if obj_type == GroupAgentItemType.CONTACT:
                tool_tip = "%s (URI: %s)" % (obj.get_display_name(), obj.uri)
                return QtCore.QVariant(tool_tip)

        elif role == QtCore.Qt.DecorationRole:
            if obj_type == GroupAgentItemType.CONTACT:
                #self.emit(QtCore.SIGNAL("update_contact_order()"))

                contact = obj
                path = contact.get_portrait_path()
                IS_ONLINE = contact.presence > UserPresence.OFFLINE_OR_INVISIBLE

                if path:
                    if obj.uri in self._portrait_cache:
                        its_cached = self._portrait_cache[contact.uri]
                        if its_cached["presence"] == contact.presence:
                            return its_cached["pixmap_widget"]

                    if IS_ONLINE:
                        pixmap_widget = QtGui.QPixmap(path)
                    else:
                        pixmap_widget = to_grayscaled(path)

                    width, height = 50, 50
                    pixmap_widget = pixmap_widget.scaled(QtCore.QSize(width, height))
                    self._add_to_cache(contact, pixmap_widget)

                    return pixmap_widget
                else:
                    if contact.presence > UserPresence.OFFLINE_OR_INVISIBLE:
                        URI = UserPresence.ONLINE
                    else:
                        URI = UserPresence.OFFLINE_OR_INVISIBLE
                    return self._portrait_cache[URI]["pixmap_widget"]


        return QtCore.QVariant()

    def _add_to_cache(self, contact, pixmap_widget):
        self._portrait_cache[contact.uri] = {
            "presence" : contact.presence,
            "pixmap_widget" : pixmap_widget,
        }

    def parent(self, child_index):
        if not child_index.isValid():
            return QtCore.QModelIndex()

        obj = child_index.internalPointer()
        if obj.get_type() == GroupAgentItemType.CONTACT:
            parent_obj = obj.get_group()
            row = self.group_agent.index(parent_obj)
            return self.createIndex(row, self.FIRST_COLUMN, parent_obj)

        return QtCore.QModelIndex()

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


class ContactListWidow(QtGui.QWidget, Ui_ContactListWindow):
    FIRST_COLUMN = 0
    def __init__(self, blah):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(LOGO_PATH))

        self.chat_history = {}

        self.blah = blah
        self.user = blah.user
        self.chat_win = ChatWindow(blah)
        self.chat_win.move(200, 200)

        self.load_user_presence_list()

        self.update_all_portraits_t = None

        # listen the socket (main sock) used in SIPC auth
        self.listen_main_sock_t = None
        self.server_push_data_list = []
        self.connect(self, QtCore.SIGNAL("recved_server_push_datas()"),
                     self.consume_server_push_datas)

        self.conversation_server_push_data_list = []
        self.connect(self, QtCore.SIGNAL("recved_conversation_server_push_datas()"),
                     self.consume_conversation_server_push_datas)

        self.setup_keep_alive_timer()
        self.setup_check_user_presence_timer()

        self._init_addition_widgets()

        i_subscribe_contact_list(self.user, debug = True)

        self.listen_main_sock_t_run()
        self.keep_alive_timer.start()

    def on_contact_list_double_clicked(self):
        contact = self.get_current_selected_contact()
        DOUBLE_CLICK_ON_CONTACT_ITEM = contact is not None
        if DOUBLE_CLICK_ON_CONTACT_ITEM:
            self.goto_or_create_tab_before_send_msg(contact)

    def _init_addition_widgets(self):
        self.nicknameLabel.setText(self.blah.get_my_name())
        self.set_user_presence()
        self._init_portrait_widget()

        self.contact_list_tree_model = ContactListTreeModel(self.user.group_agent)
        self.contact_list_tree_view.setModel(self.contact_list_tree_model)

        self.selection_model = self.contact_list_tree_view.selectionModel()

        self.contact_list_tree_view.mouseDoubleClickEvent = contact_list_double_click_wrapper(
                self.contact_list_tree_view.mousePressEvent, self.contact_list_tree_view)
        self.connect(self.contact_list_tree_view, QtCore.SIGNAL('doubleClicked()'),
                     self.on_contact_list_double_clicked)

        self.contact_list_tree_view.mouseReleaseEvent = contact_list_view_left_click_wrapper(
                self.contact_list_tree_view.mouseReleaseEvent, self.contact_list_tree_view)
        self.connect(self.contact_list_tree_view, QtCore.SIGNAL("leftClicked()"),
                     self.on_contact_group_left_clicked)

#        self.connect(self.contact_list_tree_model,
#            QtCore.SIGNAL('update_contact_order()'),
#            self.update_contact_order_after_presence_changed)

        self.update_portraits_t_run()

        self.reportBugBtn.clicked.connect(self.on_report_bug_btn_click)
        self.add_buddy_btn.clicked.connect(self.on_add_buddy_btn_click)

#    def update_contact_order_after_presence_changed(self):
#        logger.info('data_change')

    def on_contact_group_left_clicked(self):
        idx = self.selection_model.currentIndex()
        obj = idx.internalPointer()
        if obj and obj.get_type() == GroupAgentItemType.GROUP:
            if self.contact_list_tree_view.isExpanded(idx):
                self.contact_list_tree_view.collapse(idx)
            else:
                self.contact_list_tree_view.expand(idx)


    def update_portraits_t_run(self):
        if self.update_all_portraits_t and not self.update_all_portraits_t.isFinished():
            return
        self.update_all_portraits_t = IThread(i_update_all_portraits, user = self.user)
        self.update_all_portraits_t.start()

    def get_current_selected_contact(self):
        idx = self.selection_model.currentIndex()
        obj = idx.internalPointer()
        if obj and obj.get_type() == GroupAgentItemType.CONTACT:
            return obj

    def on_avatar_left_clicked(self):
        read_only = True
        user = self.blah.user
        is_save_btn_clicked, new_user = ProfileDialog.get_data(self, user, read_only)
        assert new_user != None

    def _init_portrait_widget(self):
        self.set_portrait()
        self.portraitLabel.mousePressEvent = portrait_left_click_wrapper(self.portraitLabel.mousePressEvent,
                                                                         self.portraitLabel)
        self.connect(self.portraitLabel, QtCore.SIGNAL('leftClicked()'), self.on_avatar_left_clicked)

        self.set_portrait()

    def set_portrait(self, path = None):
        if not path:
            path = self.user.get_portrait_path() or DEFAULT_PORTRAIT_PATH
        elif path and not os.path.exists(path):
            self.download_portrait_t = IThread(i_download_portrait_by_uri,
                    user = self.user, uri = self.user.uri, debug = True)
            self.connect(self.download_portrait_t, QtCore.SIGNAL("thread_finished()"),
                    self.download_portrait_t_finished)
            self.download_portrait_t.start()
        pixmap = QtGui.QPixmap(path)
        width, height = 60, 60
        pixmap = pixmap.scaled(QtCore.QSize(width, height))
        self.portraitLabel.setPixmap(pixmap)

    def download_portrait_t_finished(self):
        res_obj = self.download_portrait_t.get_return()
        assert res_obj != None

    def on_add_buddy_btn_click(self):
        myname = "" # self.user.nickname[:10]
        send_btn_clicked, data = AddBuddyDialog.get_data(parent = self, name = myname)
        if send_btn_clicked:
            i_add_buddy(self.user, data["account"], data["name"], debug = True)


    def on_report_bug_btn_click(self):
        popup_about(self)

    def switch_presence_to_online(self):
        pass

    def switch_presence_to_away(self):
        pass

    def switch_presence_to_invisible(self):
        pass

    def switch_presence_to_offline(self):
        logger.error("in switch_presence_to_offline()")
        # there are bug in timer ?
        # QObject::startTimer: QTimer can only be used with threads started with QThread
        self.check_user_presence_timer.stop()
        self.keep_alive_timer.stop()

        convs = self.user.get_conversations()
        uri_list = convs.keys()
        for uri in uri_list:
            conv = convs[uri]
            conv.over()
            convs.pop(uri)

        sock = self.user.get_sock()
        sock.close()

        while not self.listen_main_sock_t.isFinished():
            time.sleep(0.1)

        while not self.update_all_portraits_t.isFinished():
            time.sleep(0.1)

        self.hide()
        self.blah.show()
        self.blah.show_or_hide_login_widgets(show = True)

    def load_user_presence_list(self):
        for const, presence in UserPresence.__dict__["CONST_TO_STR_ZH"].iteritems():
            self.presenceComboBox.addItem(presence, QtCore.QVariant(const))

        self.connect(self.presenceComboBox, QtCore.SIGNAL('currentIndexChanged ( int )'),
                        self.on_presence_changed)

    def on_presence_changed(self, idx):
        presence_const = self.presenceComboBox.itemData(idx).toInt()[0]
        i_set_presence(self.user, presence_const)

        self.set_presence_icon(presence_const)

    def set_presence_icon(self, presence_const):
        #icon_path = os.path.join(ICON_PATH, "status-%s.png" % str(UserPresence(presence_const)))
        icon_path = ":/status-%s.png" % str(UserPresence(presence_const))
        self.presenceLabel.setPixmap(QtGui.QPixmap(icon_path))

    def set_user_presence(self):
        idx = self.presenceComboBox.findData(QtCore.QVariant(self.user.get_presence()))
        self.presenceComboBox.setCurrentIndex(idx)

        self.set_presence_icon(self.user.get_presence())

    def check_user_presence(self):
        if self.user.get_presence() == UserPresence.OFFLINE:
            logger.error('user.get_presence() == UserPresence.OFFLINE is True')
            self.switch_presence_to_offline()

    def consume_server_push_datas(self):
        while len(self.server_push_data_list):
            res_obj, sock = self.server_push_data_list.pop()
            self._consume_datas(res_obj, sock)

    def consume_conversation_server_push_datas(self):
        while len(self.conversation_server_push_data_list):
            res_obj, sock = self.conversation_server_push_data_list.pop()
            self._consume_datas(res_obj, sock)

    def _consume_notification(self, res_obj, sock):
        assert (sock is not None)
        sip_event_str = res_obj.headers.get_field_value("N")
        sip_event = SIPEvent.get_const_by_str(SIPEvent, sip_event_str)
        events = get_conversation_events(res_obj)

        body_dom = minidom.parseString(res_obj.body)
        CONTACT_PRESENCE_CHANGED = sip_event == SIPEvent.PRESENCE_V4 and \
                                   NotificationEvent.PRESENCE_CHANGED in events

        CONTACT_LEFT = sip_event == SIPEvent.CONVERSATION and \
                       NotificationEvent.USER_LEFT in events

        SYNC_USER_INFO_V4 = sip_event == SIPEvent.SYNC_USER_INFO_V4 and \
                        NotificationEvent.SYNC_USER_INFO in events

        BEEN_DISCONNECTED = sip_event == SIPEvent.REGISTRATION and \
                                NotificationEvent.DEREGISTRATION in events

        ADD_BUDDY_REFUSED = sip_event == SIPEvent.SYSTEM_NOTIFY_V4 and \
                            NotificationEvent.ADD_BUDDY_REFUSED in events

        USER_DYNAMICS_CHANGED = sip_event == SIPEvent.SYSTEM_NOTIFY_V4 and \
                                NotificationEvent.USER_DYNAMICS_CHANGED

        ADD_BUDDY_APPLICATION = sip_event == SIPEvent.CONTACT and \
                                NotificationEvent.ADD_BUDDY_APPLICATION in events

        convs = self.user.get_conversations()
        if CONTACT_PRESENCE_CHANGED:
            offline_uri_list = update_contacts_presence_from_response(self.user, body_dom)
            for uri in offline_uri_list:
                if uri in convs:
                    conv = convs[uri]
                    assert conv.sock != self.user.get_sock()
                    conv.over()
                    #convs.pop(uri)
            self.update_portraits_t_run()

            self.emit(QtCore.SIGNAL('dataChanged ( const QModelIndex & , const QModelIndex &  )'))

        elif CONTACT_LEFT:
            member_nodes = body_dom.getElementsByTagName("member")
            for member_node in member_nodes:
                uri = member_node.getAttribute("uri")
                conv = convs[uri]
                assert conv.sock != self.user.get_sock()
                conv.over()
                #convs.pop(uri)

        elif SYNC_USER_INFO_V4:
            self._consume_noti_sync_user_info_v4(res_obj)

        elif BEEN_DISCONNECTED:
            OFFLINE_ALERTS = "You have been disconnected" \
                "as someone has signed in with your ID on another computer." \
                "<br /><br />" \
                "Please note that if this was not intentional, some may have stolen your passwrod. "\
                "Please change your password."
            popup_error(self, OFFLINE_ALERTS)
            self.switch_presence_to_offline()
            #"Sign in again", "OK"

        elif ADD_BUDDY_REFUSED:
            uri, reason = i_parse_add_buddy_refused(body_dom)
            assert uri != reason
            logger.error("User (URI: %s) refused your add buddy application, reason: %s" % (uri, reason))

        elif ADD_BUDDY_APPLICATION:
            self._consume_add_buddy_application(res_obj)

        elif USER_DYNAMICS_CHANGED:
            pass

    def update_portraits(self):
        for contact in self.user.group_agent.get_all_contacts():
            if contact.image_changed == YES:
                i_download_portrait_by_uri(self.user, contact.uri)
                contact.image_changed = NO

    def _consume_add_buddy_application(self, res_obj):
        body_dom = minidom.parseString(res_obj.body)
        app_data = i_parse_add_buddy_application(body_dom)

        sid = get_sid_from_uri(app_data["uri"])
        SHOW_MSG_TPL = u"我是 %s (飞信号: %s )，想添加您为好友"
        show_msg = SHOW_MSG_TPL % (app_data["who"], sid)

        send_btn_clicked, data = ReplyAddBuddyDialog.get_data(parent = self,
                                        show_msg = show_msg)

        if send_btn_clicked:
            if data["accept"]:
                result = ReplyAddBuddyApplication.ACCEPT
            else:
                result = ReplyAddBuddyApplication.REFUSE
        else:
            result = ReplyAddBuddyApplication.IGNORE

        i_reply_add_buddy(self.user, res_obj, result,
                          data["refuse_reason"], data["decline_add_req_forever"],
                          debug = True)

    def _consume_noti_sync_user_info_v4(self, res_obj):
        body_dom = minidom.parseString(res_obj.body)

        contact_list_nodes = body_dom.getElementsByTagName("contact-list")
        if not contact_list_nodes:
            return
        assert len(contact_list_nodes) == 1
        contact_list_node = contact_list_nodes[0]
        contact_list_version = contact_list_node.getAttribute("version")
        if self.user.contact_list_version != contact_list_version:
            self.user.contact_list_version = contact_list_version

        buddy_nodes = body_dom.getElementsByTagName("buddy")
        for buddy_node in buddy_nodes:
            attr = buddy_node.getAttribute
            user_id = attr("user-id")
            contact = self.user.group_agent.get_contact_by_user_id(user_id)

            # someone send add buddy application to you,
            # and you send buddy application before any reply,
            # contact will be not found in self.user.contact_list.
            if not contact:
                continue

            if attr("action") == "remove":
                logger.error("!!! Your buddy (uri: %s) %s you" % (contact.uri, attr("action")))

                convs = self.user.conversations()
                conv = convs.get(contact.uri, None)
                if conv:
                    assert conv.sock != self.user.get_sock()
                    conv.over()
                    del conv
                self.user.group_agent.remove_user_by_user_id(user_id)

            elif attr("action") == "add":
                logger.info("!!! Your buddy (uri: %s) %s you" % (contact.uri, attr("action")))

                cat = Contact(user = self.blah.user)
                map_node_attr_to_obj(buddy_node, cat)
                self.user.contact_list.append(cat)
                cat.buddy_lists = attr("buddy-lists")
                cat.online_notify = attr("online-notify")
                cat.permission_values = attr("permission-values")

    def _consume_invitation(self, res_obj, sock):
        assert (sock is not None)

        """ TODO: ignore invitation will prevent from hide detecting. """
        i_send_ack(res_obj, sock)

        attr = res_obj.headers.get_field_value
        from_uri = attr("F")

        conv = Conversation(from_uri)
        convs = self.user.get_conversations()
        convs[from_uri] = conv
        get_sock_for_recv_msg_thread = IThread(get_sock_for_recv_msg, user = self.user, res_obj = res_obj,
                                      debug = True)
        conv.get_sock_for_recv_msg_thread = get_sock_for_recv_msg_thread
        self.connect(conv.get_sock_for_recv_msg_thread, QtCore.SIGNAL("thread_finished()"),
                     self.recv_msg_t_finished)
        conv.get_sock_for_recv_msg_thread.start()

    def recv_msg_t_finished(self):
        convs_d = dict()
        convs = self.user.get_conversations()
        for to_uri, conv in convs.iteritems():
            if conv.get_sock_for_recv_msg_thread and conv.get_sock_for_recv_msg_thread.isFinished():
                res_obj = conv.get_sock_for_recv_msg_thread.get_return()
                conv.get_sock_for_recv_msg_thread = None

                if res_obj.code == SIPResponse.OK:
                    assert conv.sock != self.user.get_sock()
                    assert conv.listen_thread == None
                    self.add_listener_for_conversation_sock(conv)
                    convs_d[to_uri] = conv
            else:
                convs_d[to_uri] = conv

        self.user.set_conversations(convs_d)

    def add_listener_for_conversation_sock(self, conv):
        assert conv.sock != self.user.get_sock()
        conv.listen_thread = IThread(self.listen_sock,
                sock = conv.sock,
                data_list = self.conversation_server_push_data_list,
                signal = 'recved_conversation_server_push_datas()',
                debug = True)
        conv.listen_thread.start()

        conv.keep_conn_busy_thread = PeriodicExecutor(30, i_keep_connection_busy,
                                                      user = self.user,
                                                      sock = conv.sock)
        conv.keep_conn_busy_thread.start()

    def _consume_message(self, res_obj, sock):
        assert (sock is not None)

        attr = res_obj.headers.get_field_value
        from_uri = attr("F")

        logger.info("Get message from: %s" % from_uri)

        msg = rm_markups(to_unicode_obj(res_obj.body))

        if from_uri != SERVICE_PROVIDER_URI:
            i_send_ack(res_obj, sock)
            contact = self.user.group_agent.get_contact_by_uri(from_uri)
            if not contact:
                """ This message send you before him delete you from his buddy list. """
                name = u"陌生人 (飞信号: %s) " % get_sid_from_uri(from_uri)
            else:
                name = contact.get_display_name()
        else:
            name = to_unicode_obj("系统信息")

        self.goto_or_create_tab_after_received_msg(from_uri)

        chat_history_model = self.chat_history[from_uri]
        self.chat_win.append_to_chat_history(chat_history_model, name, msg, OTHER_LOG_TPL)

    def goto_or_create_tab_after_received_msg(self, from_uri):
        IS_SYSTEM_MSG = from_uri.find('sip:') == STR_NOT_FOUND

        if not IS_SYSTEM_MSG:
            TAB_ALREADY_EXISTS = self.chat_win.go_to_tab_by_uri(from_uri)
            if not TAB_ALREADY_EXISTS:
                self.chat_win.create_tab(from_uri)

    def _consume_datas(self, res_obj, sock):
        sip_type = res_obj.get_sip_method()
        
        if sip_type == SIP.NOTIFICATION:
            self._consume_notification(res_obj, sock)
        elif sip_type == SIP.SIPC_4_0:
            i_process_sipc_request_response(self.user, res_obj)
        elif sip_type == SIP.INVITATION:
            self._consume_invitation(res_obj, sock)
        elif sip_type == SIP.MESSAGE:
            self._consume_message(res_obj, sock)

#        elif sip_type == SIP.INCOMING:
#            process_incoming(user, res_obj)

    def send_keep_connection_busy(self, sock, debug = False):
        i_keep_connection_busy(self.user, sock, debug)
#        try:
#            i_keep_connection_busy(self.user, sock, debug)
#        except socket.error as (err_no, err_msg):
#            assert err_msg != None
#            # `socket.error: [Errno 22] Invalid argument` exception means disconnect
#            if err_no == errno.EINVAL:
#                self.user.get_presence() = OFFLINE
#                time.sleep(1)

    def send_keep_alive(self, debug = False):
        i_send_keep_alive(self.user, debug)
#        try:
#            i_send_keep_alive(self.user, debug)
#        except socket.error as (err_no, err_msg):
#            assert err_msg != None
#            # `socket.error: [Errno 22] Invalid argument` exception means disconnect
#            if err_no == errno.EINVAL:
#                self.user.get_presence() = OFFLINE
#                time.sleep(1)

    def setup_keep_alive_timer(self):
        self.keep_alive_timer = QtCore.QTimer()
        self.connect(self.keep_alive_timer, QtCore.SIGNAL('timeout()'), self.send_keep_alive)
        msec = 1000 * 70
        self.keep_alive_timer.setInterval(msec)

    def setup_check_user_presence_timer(self):
        print " in setup_check_user_presence_timer() "
        self.check_user_presence_timer = QtCore.QTimer()
        self.connect(self.check_user_presence_timer, QtCore.SIGNAL('timeout()'), self.check_user_presence)
        msec = 1000 * 5
        self.check_user_presence_timer.setInterval(msec)

    def listen_main_sock_t_run(self):
        """ TODO: offline-handler
        socket.error: [Errno 32] Broken pipe
        """
        # listen the socket (main sock) used in SIPC auth
        self.listen_main_sock_t = IThread(self.listen_sock, sock = self.user.get_sock(),
                data_list = self.server_push_data_list,
                signal = 'recved_server_push_datas()',
                debug = True)
        self.listen_main_sock_t.start()

        # self.connect(self.listen_main_sock_t, QtCore.SIGNAL('thread_finished()'), self.switch_presence_to_offline)

    def listen_sock(self, sock, data_list, signal, debug = False):
        IS_MAIN_SOCK = sock is self.user.get_sock()
        if IS_MAIN_SOCK:
            is_main_sock = 'yes'
        else:
            is_main_sock = 'no'
        recv_buf = ""

        while True:
            try:
                readys = select.select([sock], [], [sock])
            except select.error as (err_no, err_msg):
                # sock passive close but listen thread still running
                logger.error("!!! %s while select, is main sock: %s" % (err_msg, is_main_sock))
                SOCK_CLOSED_T_RUNNING = (not IS_MAIN_SOCK) and (err_no == errno.EBADF)
                if SOCK_CLOSED_T_RUNNING:
                    return SOCK_CLOSED_T_RUNNING
            except socket.error as (err_no, err_msg):
                logger.error("!!! %s while select, is main sock: %s" % (err_msg, is_main_sock))
                DEREGISTERED = IS_MAIN_SOCK and (err_no == errno.EBADF)
                return DEREGISTERED

            input_ready = readys[0]
            except_ready = readys[2]

            if except_ready:
                logger.error("!!! Get exception while read socket")
                raise Exception("get exception while read socket")

            if input_ready:
                buf = ""
                try:
                    """ NOTICE: don't set size_once less than 1024, or you will get errno.EAGAIN and
                      this sock will couldn't read data again. """
                    buf = SIPConnection.recv(sock, size_once = 1024, flags = socket.MSG_DONTWAIT, debug = debug)
                except socket.error as (err_no, err_msg):
                    if err_no == errno.EAGAIN:
                        logger.error("!!! %s while sock.recv, is main sock: %s" % (err_msg, is_main_sock))
                        
                        res = is_a_complete_response(recv_buf)
                        CONTINUE_RECV = len(recv_buf) != 0 and res == SIPResponseValidity.NOT_COMPLETE
                        if CONTINUE_RECV:
                            print "CONTINUE_RECV:", CONTINUE_RECV
                            continue

                recv_buf += buf
                """Contact left conversation with a `UserLeft` push msg will be active close sock(i),
                this sock will receives nothing after `UserLeft`, so length of buf will be zero.

                This sock will be active close if get deregistered event type of registration notification,
                so length of buf will be zero too.
                """
                if len(recv_buf) == 0:
                    if not IS_MAIN_SOCK:
                        logger.error("!!! len(recv_buf) == 0, is main sock: %s", is_main_sock)
                        return
                else:
                    pkgs, remain = split_package(recv_buf)

                    while len(pkgs):
                        res_obj = pkgs.pop(0)
                        data_list.append((res_obj, sock))
                        self.emit(QtCore.SIGNAL(signal))
                    recv_buf = remain
                    

    def keyPressEvent(self, event):
        key = event.key()
        modifier = event.modifiers()
        DELETE_BUDDY = (modifier == QtCore.Qt.ControlModifier) and (key == QtCore.Qt.Key_Backspace)
        OPEN_CHAT_WIN = key == QtCore.Qt.Key_Return
        VIEW_PROFILE = (modifier == QtCore.Qt.ControlModifier) and (key == QtCore.Qt.Key_I)

        if OPEN_CHAT_WIN:
            contact = self.get_current_selected_contact()
            PRESS_ENTER_ON_CONTACT_ITEM = contact is not None
            if PRESS_ENTER_ON_CONTACT_ITEM:
                self.goto_or_create_tab_before_send_msg(contact)

        elif DELETE_BUDDY:
#            item = self.selection_model.selectedItems()[0]
#            uri = str(item.data(self.FIRST_COLUMN, QtCore.Qt.UserRole).toString())
#            IS_BUDDY_ITEM = uri.find('sip:') != STR_NOT_FOUND
#            if IS_BUDDY_ITEM:
            uri = self._get_current_selected_uri()
            if uri:
                self.delete_buddy(uri)

        elif VIEW_PROFILE:
            uri = self._get_current_selected_uri()
            if uri:
                user = self.user.group_agent.get_contact_by_uri(uri)
                read_only = True
                ProfileDialog.get_data(self, user, read_only)

    def _get_current_selected_uri(self):
        contact = self.get_current_selected_contact()
        IS_BUDDY_ITEM = contact.uri.find('sip:') != STR_NOT_FOUND
        if IS_BUDDY_ITEM:
            return contact.uri

    def delete_buddy(self, uri):
        cat = self.user.group_agent.get_contact_by_uri(uri)
        SHOW_MSG = to_unicode_obj("%s (飞信号： %s)")
        show_msg = SHOW_MSG % (cat.nickname, cat.sid)
        sure_btn_clicked, data = DeleteBuddyDialog.get_data(parent = self, show_msg = show_msg)
        if sure_btn_clicked:
            i_delete_buddy(self.user, cat.uri, data["delete_both"], debug = True)


    def goto_or_create_tab_before_send_msg(self, contact_item):
        if hasattr(contact_item, "data"):
            column = self.FIRST_COLUMN
            contact_uri = str(contact_item.data(column, QtCore.Qt.UserRole).toString())
        else:
            contact_uri = contact_item.uri

        IS_SYSTEM_MSG = contact_uri.find('sip:') == STR_NOT_FOUND

        if not IS_SYSTEM_MSG:
            TAB_ALREADY_EXISTS = self.chat_win.go_to_tab_by_uri(contact_uri)
            if not TAB_ALREADY_EXISTS:
                self.chat_win.create_tab(contact_uri)


def update_contacts_presence_from_response(user, body_dom):
    """ Notice: you will get your presence changed notification if yours changed.

        return [is_offline_uri, ...] """
    contact_nodes = body_dom.getElementsByTagName("c")
    offline_list = []

    for contact_node in contact_nodes:
        user_id = contact_node.getAttribute("id")
        cat = user.group_agent.get_contact_by_user_id(user_id)
        if not cat:
            continue
        exists = contact_node.getElementsByTagName("p")
        if exists:
            p_node = exists[0]
            attr = p_node.getAttribute

            cat.mobile_no = attr("m")
            cat.score_level = attr("l")
            cat.nickname = attr("n")
            cat.impresa = attr("i")

            portrait_crc = attr("p").strip()
            if portrait_crc is not None and portrait_crc != "":
                portrait_crc = int(portrait_crc)
                if cat.portrait_crc == portrait_crc or 0 == portrait_crc:
                    cat.image_changed = NO
                else:
                    cat.image_changed = YES
                cat.portrait_crc = portrait_crc
            else:
                cat.image_changed = NO

            cat.carrier = attr("c")
            cat.carrier_status = attr("cs")
            cat.service_status = attr("s")

        exists = contact_node.getElementsByTagName("pr")
        if exists:
            pr_node = exists[0]
            attr = pr_node.getAttribute

            dt = attr("dt")
            if dt == "":
                cat.device_type = "PC"
            else:
                cat.device_type = dt

            presence = attr("b")
            if presence:
                cat.presence = int(presence)
                if cat.presence == UserPresence.OFFLINE_OR_INVISIBLE:
                    offline_list.append(cat.uri)

    #user.group_agent.sort()

    return offline_list