# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/lee/backups/code/iblah_py/ui/ui_reply_add_buddy_dialog.ui'
#
# Created: Fri May  6 21:47:58 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ReplyAddBuddyDialog(object):
    def setupUi(self, ReplyAddBuddyDialog):
        ReplyAddBuddyDialog.setObjectName(_fromUtf8("ReplyAddBuddyDialog"))
        ReplyAddBuddyDialog.resize(450, 340)
        self.msg_text_edit = QtGui.QTextEdit(ReplyAddBuddyDialog)
        self.msg_text_edit.setEnabled(False)
        self.msg_text_edit.setGeometry(QtCore.QRect(20, 30, 411, 51))
        self.msg_text_edit.setObjectName(_fromUtf8("msg_text_edit"))
        self.groupBox = QtGui.QGroupBox(ReplyAddBuddyDialog)
        self.groupBox.setGeometry(QtCore.QRect(20, 100, 411, 161))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.reason_line_edit = QtGui.QLineEdit(self.groupBox)
        self.reason_line_edit.setEnabled(False)
        self.reason_line_edit.setGeometry(QtCore.QRect(120, 90, 241, 22))
        self.reason_line_edit.setObjectName(_fromUtf8("reason_line_edit"))
        self.accept_radio_btn = QtGui.QRadioButton(self.groupBox)
        self.accept_radio_btn.setGeometry(QtCore.QRect(30, 30, 102, 20))
        self.accept_radio_btn.setObjectName(_fromUtf8("accept_radio_btn"))
        self.decline_add_req_check_box = QtGui.QCheckBox(self.groupBox)
        self.decline_add_req_check_box.setEnabled(False)
        self.decline_add_req_check_box.setGeometry(QtCore.QRect(60, 120, 141, 20))
        self.decline_add_req_check_box.setObjectName(_fromUtf8("decline_add_req_check_box"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setEnabled(True)
        self.label.setGeometry(QtCore.QRect(60, 90, 62, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.refuse_radio_btn = QtGui.QRadioButton(self.groupBox)
        self.refuse_radio_btn.setGeometry(QtCore.QRect(30, 60, 102, 20))
        self.refuse_radio_btn.setObjectName(_fromUtf8("refuse_radio_btn"))
        self.send_btn = QtGui.QPushButton(ReplyAddBuddyDialog)
        self.send_btn.setEnabled(True)
        self.send_btn.setGeometry(QtCore.QRect(320, 280, 114, 32))
        self.send_btn.setObjectName(_fromUtf8("send_btn"))

        self.retranslateUi(ReplyAddBuddyDialog)
        QtCore.QObject.connect(self.send_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), ReplyAddBuddyDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(ReplyAddBuddyDialog)

    def retranslateUi(self, ReplyAddBuddyDialog):
        ReplyAddBuddyDialog.setWindowTitle(QtGui.QApplication.translate("ReplyAddBuddyDialog", "回应添加好友请求", None, QtGui.QApplication.UnicodeUTF8))
        self.msg_text_edit.setHtml(QtGui.QApplication.translate("ReplyAddBuddyDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Lucida Grande\'; font-size:13pt;\">12314124</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("ReplyAddBuddyDialog", "回应", None, QtGui.QApplication.UnicodeUTF8))
        self.accept_radio_btn.setText(QtGui.QApplication.translate("ReplyAddBuddyDialog", "同意", None, QtGui.QApplication.UnicodeUTF8))
        self.accept_radio_btn.setShortcut(QtGui.QApplication.translate("ReplyAddBuddyDialog", "Ctrl+A", None, QtGui.QApplication.UnicodeUTF8))
        self.decline_add_req_check_box.setText(QtGui.QApplication.translate("ReplyAddBuddyDialog", "拒绝此人再和我联系", None, QtGui.QApplication.UnicodeUTF8))
        self.decline_add_req_check_box.setShortcut(QtGui.QApplication.translate("ReplyAddBuddyDialog", "Ctrl+D", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ReplyAddBuddyDialog", "拒绝理由", None, QtGui.QApplication.UnicodeUTF8))
        self.refuse_radio_btn.setText(QtGui.QApplication.translate("ReplyAddBuddyDialog", "不同意", None, QtGui.QApplication.UnicodeUTF8))
        self.refuse_radio_btn.setShortcut(QtGui.QApplication.translate("ReplyAddBuddyDialog", "Ctrl+R", None, QtGui.QApplication.UnicodeUTF8))
        self.send_btn.setText(QtGui.QApplication.translate("ReplyAddBuddyDialog", "发送 (&S)", None, QtGui.QApplication.UnicodeUTF8))
        self.send_btn.setShortcut(QtGui.QApplication.translate("ReplyAddBuddyDialog", "Return", None, QtGui.QApplication.UnicodeUTF8))

