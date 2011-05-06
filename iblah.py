#!/usr/bin/env python
#coding:utf-8
import httplib
import os
import sys
import traceback
#from pprint import pprint as pp

from PyQt4 import QtGui
from PyQt4 import QtCore
from libblah.config import i_download_sys_config, i_update_user_after_get_sys_config_success
from libblah.http import HTTPResponse
from libblah.sipc_auth import i_update_user_after_sipc_auth_success, i_sipc_auth
from libblah.ssi_auth import i_update_user_after_ssi_auth_success, i_ssi_auth
from libblah.user import i_create_user, i_hash_passwd
from libblah.consts import MAX_RETRY_TIMES, UserPresence
from libblah import consts
from libblah.log import logger
from libblah.store import get_last_login_sid, get_accounts_basic_info_list
from libblah.sip import SIPResponse
from libblah.verification import i_generate_verification_pic
from libiblah.check_environ import check_runtime
from libiblah.contact_list_win import ContactListWidow
from libiblah.popup_dlgs import GetVerificationDialog, popup_about, popup_error
from libiblah.qthread import IThread, kill_qthread, IThreadKiller
from libiblah.const import LOGO_PATH
from libiblah.style import get_best_font, set_font
from ui.ui_login import Ui_LoginWindow

osp = os.path


class IBlah(QtGui.QMainWindow, Ui_LoginWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(LOGO_PATH))
        self.setWindowTitle(consts.NAME)
        
        self._debug_mode = None

        self.load_user_presence_list()
        self.load_account_list()

        self.user = None

        # SSI login thread
        self.ssi_auth_t = None
        self.ssi_auth_t_killer = None
        self.verification = None

        # SIPC auth thread
        self.sipc_auth_t = None
        self.sipc_auth_t_killer = None

        # download system configuration
        self.download_sys_config_t = None
        self.download_sys_config_t_killer = None

        # contact list widget
        self.contact_list_win = None

#        self.setup_tray_icon()
        self._init_misc_widgets()

        self._retry_times = 0

        self.show()

    def _init_misc_widgets(self):
        self.loginBtn.clicked.connect(self.on_login_btn_click)
        self.reportBugBtn.clicked.connect(self.on_report_bug_btn_click)

        self.progress_bar.setMaximum(0)
        self.progress_bar.setMinimum(0)
        self.progress_bar.hide()

        self.debug_mode_cb.hide()

    def get_my_name(self):
        return self.user.nickname or self.user.sid
        

    def load_account_list(self):
        self.accounts_basic_info_list = get_accounts_basic_info_list()

        for acc in self.accounts_basic_info_list:
            if acc["mobile_no"]:
                self.accountComboBox.addItem(acc["mobile_no"], QtCore.QVariant(acc["sid"]))
            else:
                self.accountComboBox.addItem(acc["sid"], QtCore.QVariant(acc["sid"]))

        self.connect(self.accountComboBox,
                     QtCore.SIGNAL('currentIndexChanged ( int )'),
                     self.on_account_combobox_index_changed)
        self.connect(self.accountComboBox,
                     QtCore.SIGNAL('editTextChanged ( const QString & )'),
                     self.on_account_combobox_text_changed)

        self.on_account_combobox_index_changed(self.accountComboBox.currentIndex())

        last_login_sid = get_last_login_sid()
        if last_login_sid:
            idx = self.accountComboBox.findData(QtCore.QVariant(last_login_sid))
            self.accountComboBox.setCurrentIndex(idx)

    def load_user_presence_list(self):
        for const, presence in UserPresence.__dict__["CONST_TO_STR_ZH"].iteritems():
            self.presenceComboBox.addItem(presence, QtCore.QVariant(const))
            self.set_debault_presence()

    def set_debault_presence(self):
        idx = self.presenceComboBox.findData(QtCore.QVariant(UserPresence.ONLINE))
        self.presenceComboBox.setCurrentIndex(idx)
        
    def on_account_combobox_index_changed(self, idx):
        account_no = str(self.accountComboBox.itemText(idx))
        self._fill_correspond_by_account_no(account_no)

    def _fill_correspond_by_account_no(self, account_no):
        for acc_basic_info in self.accounts_basic_info_list:
            if account_no == acc_basic_info["mobile_no"] or \
                account_no == acc_basic_info["sid"]:
                if not acc_basic_info["hashed_passwd"]:
                    self.rememberPasswdCheckBox.setCheckState(QtCore.Qt.Unchecked)
                    return
                
                passwd = acc_basic_info["hashed_passwd"]
                
                if passwd == "hash!":
                    passwd = ""
                self.passwdLineEdit.setText(passwd)
                self.rememberPasswdCheckBox.setCheckState(QtCore.Qt.Checked)

                presence = acc_basic_info["last_presence"]
                idx = self.presenceComboBox.findData(QtCore.QVariant(presence))
                self.presenceComboBox.setCurrentIndex(idx)
                return
            else:
                self.passwdLineEdit.setText("")
                self.rememberPasswdCheckBox.setCheckState(QtCore.Qt.Unchecked)
                self.set_debault_presence()

    def on_account_combobox_text_changed(self, account_no):
        self._fill_correspond_by_account_no(account_no)

    def on_report_bug_btn_click(self):
        popup_about(self)

    def download_sys_config_t_finished(self):
        kill_qthread(self.download_sys_config_t_killer)

        res_obj = self.download_sys_config_t.get_return()
        code = res_obj.code

        if code == httplib.OK:
            self.download_sys_config_t = None
            self.download_sys_config_t_killer = None
            self._retry_times = 0
            i_update_user_after_get_sys_config_success(self.user, res_obj.body)
            self.sipc_auth_t_run()
            return

        self.download_sys_config_t = None
        self.download_sys_config_t_killer = None
        self.show_or_hide_login_widgets(show = True)
        popup_error(self, "Download configuration response code: %d" % code)

    def kill_download_sys_config_t(self):
        kill_qthread(self.download_sys_config_t)

        if self._retry_times < MAX_RETRY_TIMES:
            self._retry_times += 1
            logger.error("Download configuration failed, auto re-try ...")
            self.download_sys_config_t_run()
            return

        self.verification = None
        self.user = None
        self.show_or_hide_login_widgets(show = True)

        popup_error(self, "Download configuration failed, try again later")

    def download_sys_config_t_run(self):
        kill_qthread(self.download_sys_config_t)
        kill_qthread(self.download_sys_config_t_killer)

        self.download_sys_config_t = IThread(i_download_sys_config, user = self.user, debug = True)
        self.download_sys_config_t_killer = IThreadKiller(self.download_sys_config_t, timeout = 20)

        self.connect(self.download_sys_config_t, QtCore.SIGNAL("thread_finished()"),
                     self.download_sys_config_t_finished)
        self.connect(self.download_sys_config_t_killer, QtCore.SIGNAL("kill_qthread()"),
                     self.kill_download_sys_config_t)

        self.download_sys_config_t.start()
        self.download_sys_config_t_killer.start()

    def ssi_auth_t_finished(self):
        # why not necessary to call disconnect(SIGNAL) here
        # http://doc.qt.nokia.com/4.7/qobject.html#disconnect-3
        kill_qthread(self.ssi_auth_t_killer)

        res_obj = self.ssi_auth_t.get_return()
        code = res_obj.code

        if code == httplib.OK:
            i_update_user_after_ssi_auth_success(self.user, res_obj, self.get_if_remember_passwd())

            self._retry_times = 0
            
            self.download_sys_config_t_run()

        elif code == HTTPResponse.PASSWD_ERROR:
            self.user = None
            self.show_or_hide_login_widgets(show = True)
            popup_error(self, u"密码错误")
            
        elif code in (HTTPResponse.CCPS_CHECK_ERROR, HTTPResponse.NEED_VERIFY):
            self.verification = i_generate_verification_pic(self.user, res_obj)
            body = "%s<br />%s" % (self.verification.text, self.verification.tips)
            (btn_val, chars) = GetVerificationDialog.get_input(body = body,
                        path = self.verification.picture_path)

            if btn_val:
                logger.info("(SSI auth)Input recognise chars: %s" % chars)
                self.verification.chars = chars
                self.ssi_auth_t_run()
            else:
                self.verification = None
                self.user = None
                self.show_or_hide_login_widgets(show = True)
        else:
            raise Exception("SSI authentication response code: %d" % code)

    def show_contact_list_win(self):
        self.contact_list_win = ContactListWidow(self)
        self.hide()
        self.contact_list_win.move(800, 150)
        self.contact_list_win.show()

    def kill_ssi_auth_t(self):
        if self._retry_times < MAX_RETRY_TIMES:
            self._retry_times += 1
            logger.error("SSI authentication failed, auto re-try ...")
            self.ssi_auth_t_run()
            return 

        self.verification = None
        self.user = None
        self.show_or_hide_login_widgets(show = True)

        popup_error(self, u"连接超时（SSI），请稍候再尝试")


    def sipc_auth_t_finished(self):
        kill_qthread(self.sipc_auth_t_killer)

        res_obj = self.sipc_auth_t.get_return()
        code = res_obj.code

        if code == SIPResponse.OK:
            self._retry_times = 0
            i_update_user_after_sipc_auth_success(self.user, res_obj)
            self.show_contact_list_win()
            return

        elif code == SIPResponse.EXTENSION_REQUIRED: # login location changed
            self.verification = i_generate_verification_pic(self.user, res_obj)
            body = "%s<br />%s" % (self.verification.text, self.verification.tips)
            (btn_val, chars) = GetVerificationDialog.get_input(body = body,
                        path = self.verification.picture_path)
            
            if btn_val:
                logger.info("(SIPC auth) Input recognise chars: %s" % chars)
                self.verification.chars = chars
                self.sipc_auth_t_run()
            else:
                self.verification = None
                self.user = None
                self.show_or_hide_login_widgets(show = True)

            return

        self.show_or_hide_login_widgets(show = True)
        popup_error(self, "SIPC authentication response code: %d" % code)

    def kill_sipc_auth_t(self):
        kill_qthread(self.sipc_auth_t)

        if self._retry_times < MAX_RETRY_TIMES:
            self._retry_times += 1
            logger.error("SIPC authentication failed, auto re-try ...")
            self.sipc_auth_t_run()
            return

        self.verification = None
        self.user = None
        self.show_or_hide_login_widgets(show = True)
        
        popup_error(self, u"连接超时（SIPC），请稍候再尝试")

    def on_login_btn_click(self):
        self._retry_times = 0
        account = self.get_account()
        passwd = self.get_passwd()

#        self._debug_mode = self.debug_mode_cb.checkState() == QtCore.Qt.Checked

        if not len(account) or not len(passwd):
            popup_error(self, u"帐号和密码都不能为空！")
            return
        else:
            last_char = account[-1]
            if last_char < '0' or last_char > '9':
                popup_error(self, u"您输入的不是一个有效的飞信号或者移动手机号，飞信邮箱协议暂时不兼容本软件")
                return

        hashed_passwd = i_hash_passwd(passwd)
        presence = self.get_presence()
        self.user = i_create_user(account, hashed_passwd, presence)
        self.ssi_auth_t_run()
        self.show_or_hide_login_widgets(show = False)

    def ssi_auth_t_run(self):
        kill_qthread(self.ssi_auth_t)
        kill_qthread(self.ssi_auth_t_killer)

        self.ssi_auth_t = IThread(i_ssi_auth, user = self.user, verification = self.verification, debug = True)
        self.ssi_auth_t_killer = IThreadKiller(self.ssi_auth_t, timeout = 10)

        self.connect(self.ssi_auth_t, QtCore.SIGNAL("thread_finished()"), self.ssi_auth_t_finished)
        self.connect(self.ssi_auth_t_killer, QtCore.SIGNAL('kill_qthread()'), self.kill_ssi_auth_t)

        self.ssi_auth_t.start()
        self.ssi_auth_t_killer.start()

    def sipc_auth_t_run(self):
        kill_qthread(self.sipc_auth_t)
        kill_qthread(self.sipc_auth_t_killer)

        self.sipc_auth_t = IThread(i_sipc_auth, user = self.user, verification = self.verification, debug = True)
        self.sipc_auth_t_killer = IThreadKiller(self.sipc_auth_t, timeout = 10)

        self.connect(self.sipc_auth_t, QtCore.SIGNAL("thread_finished()"), self.sipc_auth_t_finished)
        self.connect(self.sipc_auth_t_killer, QtCore.SIGNAL('kill_qthread()'), self.kill_sipc_auth_t)

        self.sipc_auth_t.start()
        self.sipc_auth_t_killer.start()

    def get_passwd(self):
        passwd = self.passwdLineEdit.text()
        return str(passwd)

    def get_account(self):
        account = self.accountComboBox.currentText()
        return str(account)

    def get_presence(self):
        idx = self.presenceComboBox.currentIndex()
        presence_const = self.presenceComboBox.itemData(idx).toInt()[0]
        return presence_const

    def get_if_remember_passwd(self):
        if_remember_passwd = self.rememberPasswdCheckBox.checkState() == QtCore.Qt.Checked
        return if_remember_passwd
    
    def get_if_debug_mode(self):
         return self._debug_mode 

    def thread_running(self):
        logger.info('thread running ... ')

    def show_or_hide_login_widgets(self, show = True):
        if show:
            self.accountLabel.show()
            self.accountComboBox.show()

            self.passwdLabel.show()
            self.passwdLineEdit.show()

            self.presenceComboBox.show()
            self.rememberPasswdCheckBox.show()

            self.loginBtn.show()
#            self.debug_mode_cb.show()
            self.reportBugBtn.show()

            self.progress_bar.hide()
        else:
            self.accountLabel.hide()
            self.accountComboBox.hide()

            self.passwdLabel.hide()
            self.passwdLineEdit.hide()

            self.presenceComboBox.hide()
            self.rememberPasswdCheckBox.hide()

            self.loginBtn.hide()
#            self.debug_mode_cb.hide()
            self.reportBugBtn.hide()

            self.progress_bar.show()


#DEBUG_MODE = True
#DEBUG_LOG_PATH = osp.join(consts.get_desktop_path(), "iBlah_debug.log")

def main():
#    global DEBUG_MODE
    check_runtime()
    app = QtGui.QApplication(sys.argv)
    set_font(app, get_best_font())
    iblah = IBlah()
    assert iblah != None
#    DEBUG_MODE = iblah.get_if_debug_mode()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

#    try:
#        main()
#    except SystemExit:
#        pass
#    except KeyboardInterrupt:
#        pass
#    except:
#        if DEBUG_MODE:
#            output = file(DEBUG_LOG_PATH, "a+")
#            traceback.print_exc(file = output)
#            output.close()



 
