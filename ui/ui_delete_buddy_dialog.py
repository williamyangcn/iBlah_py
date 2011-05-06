# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/lee/backups/code/iblah_py/ui/ui_delete_buddy_dialog.ui'
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

class Ui_DeleteBuddyDialog(object):
    def setupUi(self, DeleteBuddyDialog):
        DeleteBuddyDialog.setObjectName(_fromUtf8("DeleteBuddyDialog"))
        DeleteBuddyDialog.resize(376, 205)
        DeleteBuddyDialog.setModal(True)
        self.label = QtGui.QLabel(DeleteBuddyDialog)
        self.label.setGeometry(QtCore.QRect(20, 20, 161, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.yes_btn = QtGui.QPushButton(DeleteBuddyDialog)
        self.yes_btn.setGeometry(QtCore.QRect(110, 140, 114, 32))
        self.yes_btn.setObjectName(_fromUtf8("yes_btn"))
        self.no_btn = QtGui.QPushButton(DeleteBuddyDialog)
        self.no_btn.setGeometry(QtCore.QRect(230, 140, 114, 32))
        self.no_btn.setObjectName(_fromUtf8("no_btn"))
        self.delete_me_checkbox = QtGui.QCheckBox(DeleteBuddyDialog)
        self.delete_me_checkbox.setGeometry(QtCore.QRect(20, 110, 251, 20))
        self.delete_me_checkbox.setObjectName(_fromUtf8("delete_me_checkbox"))
        self.show_msg_text_edit = QtGui.QTextEdit(DeleteBuddyDialog)
        self.show_msg_text_edit.setEnabled(True)
        self.show_msg_text_edit.setGeometry(QtCore.QRect(30, 60, 311, 41))
        self.show_msg_text_edit.setLineWidth(1)
        self.show_msg_text_edit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.show_msg_text_edit.setLineWrapMode(QtGui.QTextEdit.WidgetWidth)
        self.show_msg_text_edit.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.show_msg_text_edit.setObjectName(_fromUtf8("show_msg_text_edit"))

        self.retranslateUi(DeleteBuddyDialog)
        QtCore.QObject.connect(self.yes_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), DeleteBuddyDialog.accept)
        QtCore.QObject.connect(self.no_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), DeleteBuddyDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DeleteBuddyDialog)

    def retranslateUi(self, DeleteBuddyDialog):
        DeleteBuddyDialog.setWindowTitle(QtGui.QApplication.translate("DeleteBuddyDialog", "删除好友", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("DeleteBuddyDialog", "您确定要删除一下好友码?", None, QtGui.QApplication.UnicodeUTF8))
        self.yes_btn.setText(QtGui.QApplication.translate("DeleteBuddyDialog", "是的", None, QtGui.QApplication.UnicodeUTF8))
        self.yes_btn.setShortcut(QtGui.QApplication.translate("DeleteBuddyDialog", "Return", None, QtGui.QApplication.UnicodeUTF8))
        self.no_btn.setText(QtGui.QApplication.translate("DeleteBuddyDialog", "否", None, QtGui.QApplication.UnicodeUTF8))
        self.no_btn.setShortcut(QtGui.QApplication.translate("DeleteBuddyDialog", "Esc", None, QtGui.QApplication.UnicodeUTF8))
        self.delete_me_checkbox.setText(QtGui.QApplication.translate("DeleteBuddyDialog", "同时将我从他(她)的好友列表中删除", None, QtGui.QApplication.UnicodeUTF8))
        self.show_msg_text_edit.setHtml(QtGui.QApplication.translate("DeleteBuddyDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Lucida Grande\'; font-size:13pt;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

