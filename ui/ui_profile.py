# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/lee/backups/code/iblah_py/ui/ui_profile.ui'
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

class Ui_ProfileDialog(object):
    def setupUi(self, ProfileDialog):
        ProfileDialog.setObjectName(_fromUtf8("ProfileDialog"))
        ProfileDialog.setEnabled(True)
        ProfileDialog.resize(470, 300)
        self.save_btn = QtGui.QPushButton(ProfileDialog)
        self.save_btn.setEnabled(True)
        self.save_btn.setGeometry(QtCore.QRect(330, 240, 114, 32))
        self.save_btn.setObjectName(_fromUtf8("save_btn"))
        self.avatar_label = QtGui.QLabel(ProfileDialog)
        self.avatar_label.setGeometry(QtCore.QRect(310, 20, 130, 130))
        self.avatar_label.setStyleSheet(_fromUtf8("border: 2px solid #ccc;"))
        self.avatar_label.setObjectName(_fromUtf8("avatar_label"))
        self.label_2 = QtGui.QLabel(ProfileDialog)
        self.label_2.setGeometry(QtCore.QRect(21, 117, 26, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.impresa_text_edit = QtGui.QTextEdit(ProfileDialog)
        self.impresa_text_edit.setGeometry(QtCore.QRect(80, 170, 361, 51))
        self.impresa_text_edit.setReadOnly(True)
        self.impresa_text_edit.setObjectName(_fromUtf8("impresa_text_edit"))
        self.fullname_line_edit = QtGui.QLineEdit(ProfileDialog)
        self.fullname_line_edit.setGeometry(QtCore.QRect(81, 117, 201, 22))
        self.fullname_line_edit.setReadOnly(True)
        self.fullname_line_edit.setObjectName(_fromUtf8("fullname_line_edit"))
        self.label_3 = QtGui.QLabel(ProfileDialog)
        self.label_3.setGeometry(QtCore.QRect(21, 21, 39, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(ProfileDialog)
        self.label_4.setGeometry(QtCore.QRect(21, 53, 39, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.cellphone_no_line_edit = QtGui.QLineEdit(ProfileDialog)
        self.cellphone_no_line_edit.setEnabled(True)
        self.cellphone_no_line_edit.setGeometry(QtCore.QRect(81, 53, 201, 22))
        self.cellphone_no_line_edit.setText(_fromUtf8(""))
        self.cellphone_no_line_edit.setObjectName(_fromUtf8("cellphone_no_line_edit"))
        self.fetion_no_line_edit = QtGui.QLineEdit(ProfileDialog)
        self.fetion_no_line_edit.setEnabled(True)
        self.fetion_no_line_edit.setGeometry(QtCore.QRect(81, 21, 201, 22))
        self.fetion_no_line_edit.setText(_fromUtf8(""))
        self.fetion_no_line_edit.setObjectName(_fromUtf8("fetion_no_line_edit"))
        self.label_5 = QtGui.QLabel(ProfileDialog)
        self.label_5.setGeometry(QtCore.QRect(21, 85, 33, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.email_line_edit = QtGui.QLineEdit(ProfileDialog)
        self.email_line_edit.setEnabled(True)
        self.email_line_edit.setGeometry(QtCore.QRect(81, 85, 201, 22))
        self.email_line_edit.setText(_fromUtf8(""))
        self.email_line_edit.setObjectName(_fromUtf8("email_line_edit"))
        self.label_6 = QtGui.QLabel(ProfileDialog)
        self.label_6.setGeometry(QtCore.QRect(21, 170, 52, 16))
        self.label_6.setObjectName(_fromUtf8("label_6"))

        self.retranslateUi(ProfileDialog)
        QtCore.QObject.connect(self.save_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), ProfileDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(ProfileDialog)

    def retranslateUi(self, ProfileDialog):
        ProfileDialog.setWindowTitle(QtGui.QApplication.translate("ProfileDialog", "Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.save_btn.setText(QtGui.QApplication.translate("ProfileDialog", "关闭", None, QtGui.QApplication.UnicodeUTF8))
        self.save_btn.setShortcut(QtGui.QApplication.translate("ProfileDialog", "Return", None, QtGui.QApplication.UnicodeUTF8))
        self.avatar_label.setText(QtGui.QApplication.translate("ProfileDialog", "avatar", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ProfileDialog", "姓名", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ProfileDialog", "飞信号", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ProfileDialog", "手机号", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("ProfileDialog", "EMail", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("ProfileDialog", "心情短语", None, QtGui.QApplication.UnicodeUTF8))

