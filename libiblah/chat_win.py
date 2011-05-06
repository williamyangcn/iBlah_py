#coding:utf-8
from PyQt4 import QtGui
from PyQt4 import QtCore
from libblah.conversation import Conversation
from libblah.log import logger

from libblah.strutils import to_unicode_obj
from libblah.consts import SERVICE_PROVIDER_URI
from libblah.message import i_send_msg
from libblah.utils import qstr_to_unicode_obj
from libiblah.popup_dlgs import popup_confirm
from libiblah.qthread import IThread

from ui.ui_chat import Ui_chatWindow


CHAT_LOG_CSS = """div {
    line-height: 27px;
}
.myself_nickname {
    color: #A52A2A;
    font-weight: bolder;
}
.other_nickname {
    margin-top: 10px;
    color: #A020F0;
    font-weight: bolder;
}
.ts {
    color: #7F7F7F;
}"""

MYSELF_LOG_TPL = '''<div><span class="myself_nickname">%s</span>&nbsp;&nbsp;<span class="ts">%s</span>
<p class="msg">%s</p></div>'''

OTHER_LOG_TPL = '''<div><span class="other_nickname">%s</span>&nbsp;&nbsp;<span class="ts">%s</span>
<p class="msg">%s</p></div>'''



def create_chat_history_model():
    qd = QtGui.QTextDocument()
    qd.setDefaultStyleSheet(CHAT_LOG_CSS)
    return qd


class ChatWindow(QtGui.QWidget, Ui_chatWindow):
    def __init__(self, blah):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.blah = blah
        self.user = self.blah.user

        self.chat_history_view = self.chatHistoryTextEdit
        self.convTab.clear()
        self.convTab.setDocumentMode(True)
        self.convTab.currentChanged.connect(self.current_tab_changed)
        self.convTab.tabBar().tabCloseRequested.connect(self.tab_close_requested)

#        self.run_monitor()

    def scroll_to_bottom_of_history_view(self):
        scroll_bar = self.chat_history_view.verticalScrollBar()
        scroll_bar.setSliderPosition(scroll_bar.maximum())

    def current_tab_changed(self, idx):
        NO_TAB = -1
        if idx == NO_TAB:
            return

        tabbar = self.convTab.tabBar()
        contact_uri = str(tabbar.tabData(idx).toString())

        """ NOTICE:
        It will emit `currentTabChanged()` after addTab called while convTab.count() = 1,
        and we have not set TabData yet at this time, I'm not sure this is a bug,
        do a litter hacking here to fix it.
        """
        if self.convTab.count() == 1 and not contact_uri:
            return

        display_name = tabbar.tabText(idx)
        self.contactNameLabel.setText(display_name)

        chat_history_model = self.blah.contact_list_win.chat_history[contact_uri]
        self.chat_history_view.setDocument(chat_history_model)
        self.scroll_to_bottom_of_history_view()

        cat_list_model = self.blah.contact_list_win.contact_list_tree_model
        pix_widget = cat_list_model.get_portrait_by_uri(contact_uri)
        self.portrait_label.setPixmap(pix_widget)

    def tab_close_requested(self, idx):
        no_input = self.convTab.widget(idx).toPlainText()
        if not no_input:
            self.convTab.removeTab(idx)
        else:
            msg = "Pressing the ESC key will close this conversation. <br />" \
                    "Are you sure you want to continue ?"
            if popup_confirm(self, msg):
                self.convTab.removeTab(idx)

        if not self.convTab.count():
            self.hide()

    def _close_current_tab(self):
        self.convTab.removeTab(self.convTab.currentIndex())
        if not self.convTab.count():
            self.hide()

    def go_to_tab_by_uri(self, contact_uri):
        if self.isHidden():
            self.show()

        tab_count = self.convTab.count()
        if not tab_count:
            return

        for idx in xrange(tab_count):
            tab_uri = str(self.convTab.tabBar().tabData(idx).toString())

            if tab_uri == contact_uri:
                self.convTab.setCurrentIndex(idx)
                self.focus_on_current_chat_tab()
                return True
        return False

    def create_chat_history_model_if_not_exists(self, contact_uri):
        if contact_uri not in self.blah.contact_list_win.chat_history:
            logger.info("create chat history model for %s" % contact_uri)
            model = create_chat_history_model()
            self.blah.contact_list_win.chat_history[contact_uri] = model

    def create_tab(self, target_uri):
        self.create_chat_history_model_if_not_exists(target_uri)

        if target_uri == SERVICE_PROVIDER_URI:
            label = to_unicode_obj("系统消息")
        else:
            contact = self.user.group_agent.get_contact_by_uri(target_uri)
            assert contact != None
            if contact:
                label = contact.get_display_name()
            else:
                label = u"陌生人 URI: %s " % target_uri

        chat_input = QtGui.QTextEdit(self)
        new_idx = self.convTab.addTab(chat_input, QtCore.QString(label))
        """ Notice:
        It will emit `currentTabChanged()` after addTab called while convTab.count() = 1,
        and we have not set TabData yet at this time, I'm not sure this is a bug,
        do a litter hacking in current_tab_changed() to fix it.
        """
        tabbar = self.convTab.tabBar()
        tabbar.setTabData(new_idx, QtCore.QVariant(QtCore.QString(target_uri)))

        self.convTab.setCurrentIndex(new_idx)
        self.focus_on_current_chat_tab()

        self.contactNameLabel.setText(QtCore.QString(label))

        """ Clean up document model sat by last send or recevie action """
        now_model = self.chat_history_view.document()
        target_model = self.blah.contact_list_win.chat_history[target_uri]
        if now_model is not target_model:
            self.chat_history_view.setDocument(target_model)

    def focus_on_current_chat_tab(self):
        self.setWindowState(QtCore.Qt.WindowActive)
        widget = self.convTab.currentWidget()
        widget.setFocus()

    def keyPressEvent(self, event):
        key = event.key()
        modifier = event.modifiers()
        is_goto_prev_tab = (modifier == QtCore.Qt.ControlModifier) and (key == QtCore.Qt.Key_BracketLeft)
        is_goto_next_tab = (modifier == QtCore.Qt.ControlModifier) and (key == QtCore.Qt.Key_BracketRight)
        is_send_msg = key == QtCore.Qt.Key_Return
        is_close_tab = key == QtCore.Qt.Key_Escape
        is_switch_tab = (modifier == QtCore.Qt.ControlModifier) and (key >= QtCore.Qt.Key_1 and key <= QtCore.Qt.Key_9)
        CHAR_START_AT = 48

        if is_close_tab:
            if not self.convTab.count():
                self.hide()
                return

            no_input = self.convTab.currentWidget().toPlainText()
            if not no_input:
                self._close_current_tab()
            else:
                msg = "Pressing the ESC key will close this conversation. <br />" \
                        "Are you sure you want to continue ?"
                if popup_confirm(self, msg):
                    self._close_current_tab()

        elif is_send_msg:
            widget = self.convTab.currentWidget()
            msg = widget.toPlainText()
            if not msg:
                return
            widget.clear()
            self.send_msg(qstr_to_unicode_obj(msg))

        elif is_switch_tab:
            count = self.convTab.count()
            k = key.real - CHAR_START_AT
            if 1 > k and k > 9:
                return
            if k < count + 1:
                self.convTab.setCurrentIndex(k - 1)
        elif is_goto_prev_tab:
            count = self.convTab.count()
            cur_idx = self.convTab.currentIndex()

            if count == 1:
                return
            elif cur_idx == 0:
                self.convTab.setCurrentIndex(count - 1)
            else:
                self.convTab.setCurrentIndex(cur_idx - 1)
        elif is_goto_next_tab:
            count = self.convTab.count()
            cur_idx = self.convTab.currentIndex()

            if count == 1:
                return
            elif (count - 1) == cur_idx:
                self.convTab.setCurrentIndex(0)
            else:
                self.convTab.setCurrentIndex(cur_idx + 1)

    def send_msg(self, msg):
        my_name = self.user.get_display_name()

        cur_idx = self.convTab.currentIndex()
        to_uri = str(self.convTab.tabBar().tabData(cur_idx).toString())
        assert to_uri not in (None, "")

        convs = self.user.get_conversations()
        if to_uri not in convs:
            conv = Conversation(to_uri)
            convs[to_uri] = conv
        else:
            conv = convs[to_uri]

        send_msg_thread = IThread(i_send_msg, user = self.user, to_uri = to_uri, msg = msg)
        conv.send_msg_thread = send_msg_thread
        self.connect(send_msg_thread, QtCore.SIGNAL("thread_finished()"), self.send_msg_t_finished)
        send_msg_thread.start()

        chat_history_model = self.blah.contact_list_win.chat_history[to_uri]
        self.append_to_chat_history(chat_history_model, my_name, msg, MYSELF_LOG_TPL)

    def send_msg_t_finished(self):
        logger.info("in send_msg_t_finished")

        convs_d = dict()
        convs = self.user.get_conversations()
        for to_uri, conv in convs.iteritems():
            if conv.send_msg_thread and conv.send_msg_thread.isFinished():
                conv.send_msg_thread = None

                CONTACT_IS_ONLINE = conv.sock and (conv.sock is not self.user.get_sock())
                if CONTACT_IS_ONLINE and not conv.listen_thread:
                    self.blah.contact_list_win.add_listener_for_conversation_sock(conv)

                convs_d[to_uri] = conv
            else:
                convs_d[to_uri] = conv

        self.user.set_conversations(convs_d)

    def append_to_chat_history(self, model, name, msg, tpl):
        now_time = str(QtCore.QTime().currentTime().toString())
        data = tpl % (name, now_time, msg)
        self.chat_history_view.setDocument(model)
        self.chat_history_view.append(QtCore.QString(data))