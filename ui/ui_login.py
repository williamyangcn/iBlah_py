# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/lee/backups/code/iblah_py/ui/ui_login.ui'
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

class Ui_LoginWindow(object):
    def setupUi(self, LoginWindow):
        LoginWindow.setObjectName(_fromUtf8("LoginWindow"))
        LoginWindow.resize(300, 500)
        LoginWindow.setMinimumSize(QtCore.QSize(300, 500))
        LoginWindow.setMaximumSize(QtCore.QSize(300, 500))
        font = QtGui.QFont()
        font.setPointSize(12)
        LoginWindow.setFont(font)
        LoginWindow.setWindowTitle(_fromUtf8(""))
        self.centralwidget = QtGui.QWidget(LoginWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.loginBtn = QtGui.QPushButton(self.centralwidget)
        self.loginBtn.setGeometry(QtCore.QRect(170, 300, 114, 32))
        self.loginBtn.setObjectName(_fromUtf8("loginBtn"))
        self.accountComboBox = QtGui.QComboBox(self.centralwidget)
        self.accountComboBox.setGeometry(QtCore.QRect(60, 120, 200, 27))
        self.accountComboBox.setEditable(True)
        self.accountComboBox.setMaxCount(64)
        self.accountComboBox.setObjectName(_fromUtf8("accountComboBox"))
        self.presenceComboBox = QtGui.QComboBox(self.centralwidget)
        self.presenceComboBox.setGeometry(QtCore.QRect(150, 230, 111, 26))
        self.presenceComboBox.setObjectName(_fromUtf8("presenceComboBox"))
        self.rememberPasswdCheckBox = QtGui.QCheckBox(self.centralwidget)
        self.rememberPasswdCheckBox.setGeometry(QtCore.QRect(90, 260, 171, 20))
        self.rememberPasswdCheckBox.setObjectName(_fromUtf8("rememberPasswdCheckBox"))
        self.passwdLineEdit = QtGui.QLineEdit(self.centralwidget)
        self.passwdLineEdit.setGeometry(QtCore.QRect(60, 180, 200, 22))
        self.passwdLineEdit.setText(_fromUtf8(""))
        self.passwdLineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.passwdLineEdit.setObjectName(_fromUtf8("passwdLineEdit"))
        self.reportBugBtn = QtGui.QToolButton(self.centralwidget)
        self.reportBugBtn.setGeometry(QtCore.QRect(180, 410, 100, 23))
        self.reportBugBtn.setObjectName(_fromUtf8("reportBugBtn"))
        self.accountLabel = QtGui.QLabel(self.centralwidget)
        self.accountLabel.setGeometry(QtCore.QRect(30, 100, 111, 16))
        self.accountLabel.setObjectName(_fromUtf8("accountLabel"))
        self.passwdLabel = QtGui.QLabel(self.centralwidget)
        self.passwdLabel.setGeometry(QtCore.QRect(30, 160, 62, 16))
        self.passwdLabel.setObjectName(_fromUtf8("passwdLabel"))
        self.progress_bar = QtGui.QProgressBar(self.centralwidget)
        self.progress_bar.setGeometry(QtCore.QRect(90, 210, 120, 23))
        self.progress_bar.setProperty(_fromUtf8("value"), 24)
        self.progress_bar.setObjectName(_fromUtf8("progress_bar"))
        self.debug_mode_cb = QtGui.QCheckBox(self.centralwidget)
        self.debug_mode_cb.setEnabled(False)
        self.debug_mode_cb.setGeometry(QtCore.QRect(30, 410, 87, 20))
        self.debug_mode_cb.setChecked(True)
        self.debug_mode_cb.setObjectName(_fromUtf8("debug_mode_cb"))
        LoginWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(LoginWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 300, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        LoginWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(LoginWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        LoginWindow.setStatusBar(self.statusbar)

        self.retranslateUi(LoginWindow)
        QtCore.QMetaObject.connectSlotsByName(LoginWindow)
        LoginWindow.setTabOrder(self.accountComboBox, self.passwdLineEdit)
        LoginWindow.setTabOrder(self.passwdLineEdit, self.presenceComboBox)
        LoginWindow.setTabOrder(self.presenceComboBox, self.rememberPasswdCheckBox)
        LoginWindow.setTabOrder(self.rememberPasswdCheckBox, self.loginBtn)
        LoginWindow.setTabOrder(self.loginBtn, self.reportBugBtn)

    def retranslateUi(self, LoginWindow):
        self.loginBtn.setText(QtGui.QApplication.translate("LoginWindow", "登录", None, QtGui.QApplication.UnicodeUTF8))
        self.loginBtn.setShortcut(QtGui.QApplication.translate("LoginWindow", "Return", None, QtGui.QApplication.UnicodeUTF8))
        self.rememberPasswdCheckBox.setText(QtGui.QApplication.translate("LoginWindow", "记住我的密码 (&R)", None, QtGui.QApplication.UnicodeUTF8))
        self.rememberPasswdCheckBox.setShortcut(QtGui.QApplication.translate("LoginWindow", "Ctrl+R", None, QtGui.QApplication.UnicodeUTF8))
        self.reportBugBtn.setText(QtGui.QApplication.translate("LoginWindow", "提交 &Bugs", None, QtGui.QApplication.UnicodeUTF8))
        self.reportBugBtn.setShortcut(QtGui.QApplication.translate("LoginWindow", "Ctrl+Shift+R", None, QtGui.QApplication.UnicodeUTF8))
        self.accountLabel.setText(QtGui.QApplication.translate("LoginWindow", "手机号或飞信号:", None, QtGui.QApplication.UnicodeUTF8))
        self.passwdLabel.setText(QtGui.QApplication.translate("LoginWindow", "密码:", None, QtGui.QApplication.UnicodeUTF8))
        self.debug_mode_cb.setToolTip(QtGui.QApplication.translate("LoginWindow", "勾选此项,出错后会生成日志\"桌面/iBlah_debug.log\",反馈有助于程序开发者改进", None, QtGui.QApplication.UnicodeUTF8))
        self.debug_mode_cb.setText(QtGui.QApplication.translate("LoginWindow", "调试模式", None, QtGui.QApplication.UnicodeUTF8))

