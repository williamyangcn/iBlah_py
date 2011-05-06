# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/lee/backups/code/iblah_py/ui/ui_add_buddy_dialog.ui'
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

class Ui_AddBuddyDialog(object):
    def setupUi(self, AddBuddyDialog):
        AddBuddyDialog.setObjectName(_fromUtf8("AddBuddyDialog"))
        AddBuddyDialog.resize(420, 190)
        AddBuddyDialog.setModal(True)
        self.SendBtn = QtGui.QPushButton(AddBuddyDialog)
        self.SendBtn.setGeometry(QtCore.QRect(310, 130, 94, 32))
        self.SendBtn.setDefault(False)
        self.SendBtn.setObjectName(_fromUtf8("SendBtn"))
        self.AccountLineEdit = QtGui.QLineEdit(AddBuddyDialog)
        self.AccountLineEdit.setGeometry(QtCore.QRect(60, 20, 158, 22))
        self.AccountLineEdit.setText(_fromUtf8(""))
        self.AccountLineEdit.setProperty(_fromUtf8("placeholderText"), _fromUtf8(""))
        self.AccountLineEdit.setObjectName(_fromUtf8("AccountLineEdit"))
        self.AccountLabel = QtGui.QLabel(AddBuddyDialog)
        self.AccountLabel.setGeometry(QtCore.QRect(20, 20, 62, 16))
        self.AccountLabel.setObjectName(_fromUtf8("AccountLabel"))
        self.label_2 = QtGui.QLabel(AddBuddyDialog)
        self.label_2.setGeometry(QtCore.QRect(210, 70, 62, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.MsgComboBox = QtGui.QComboBox(AddBuddyDialog)
        self.MsgComboBox.setGeometry(QtCore.QRect(60, 93, 291, 26))
        self.MsgComboBox.setObjectName(_fromUtf8("MsgComboBox"))
        self.NameLineEdit = QtGui.QLineEdit(AddBuddyDialog)
        self.NameLineEdit.setGeometry(QtCore.QRect(60, 62, 144, 22))
        self.NameLineEdit.setMaxLength(10)
        self.NameLineEdit.setProperty(_fromUtf8("placeholderText"), _fromUtf8(""))
        self.NameLineEdit.setObjectName(_fromUtf8("NameLineEdit"))
        self.label_4 = QtGui.QLabel(AddBuddyDialog)
        self.label_4.setGeometry(QtCore.QRect(20, 62, 26, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))

        self.retranslateUi(AddBuddyDialog)
        QtCore.QObject.connect(self.SendBtn, QtCore.SIGNAL(_fromUtf8("clicked()")), AddBuddyDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(AddBuddyDialog)

    def retranslateUi(self, AddBuddyDialog):
        AddBuddyDialog.setWindowTitle(QtGui.QApplication.translate("AddBuddyDialog", "添加好友", None, QtGui.QApplication.UnicodeUTF8))
        self.SendBtn.setText(QtGui.QApplication.translate("AddBuddyDialog", "发出申请", None, QtGui.QApplication.UnicodeUTF8))
        self.SendBtn.setShortcut(QtGui.QApplication.translate("AddBuddyDialog", "Return", None, QtGui.QApplication.UnicodeUTF8))
        self.AccountLabel.setText(QtGui.QApplication.translate("AddBuddyDialog", "帐号", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("AddBuddyDialog", ",", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("AddBuddyDialog", "我是", None, QtGui.QApplication.UnicodeUTF8))

