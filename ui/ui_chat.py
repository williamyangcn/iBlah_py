# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/lee/backups/code/iblah_py/ui/ui_chat.ui'
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

class Ui_chatWindow(object):
    def setupUi(self, chatWindow):
        chatWindow.setObjectName(_fromUtf8("chatWindow"))
        chatWindow.resize(500, 500)
        chatWindow.setMinimumSize(QtCore.QSize(500, 500))
        font = QtGui.QFont()
        font.setPointSize(12)
        chatWindow.setFont(font)
        chatWindow.setLocale(QtCore.QLocale(QtCore.QLocale.Chinese, QtCore.QLocale.China))
        self.convTab = QtGui.QTabWidget(chatWindow)
        self.convTab.setGeometry(QtCore.QRect(10, 330, 480, 130))
        self.convTab.setLocale(QtCore.QLocale(QtCore.QLocale.Chinese, QtCore.QLocale.China))
        self.convTab.setTabPosition(QtGui.QTabWidget.South)
        self.convTab.setTabShape(QtGui.QTabWidget.Rounded)
        self.convTab.setUsesScrollButtons(False)
        self.convTab.setTabsClosable(True)
        self.convTab.setObjectName(_fromUtf8("convTab"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.convTab.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.convTab.addTab(self.tab_2, _fromUtf8(""))
        self.chatHistoryTextEdit = QtGui.QTextEdit(chatWindow)
        self.chatHistoryTextEdit.setGeometry(QtCore.QRect(10, 80, 480, 240))
        self.chatHistoryTextEdit.setLocale(QtCore.QLocale(QtCore.QLocale.Chinese, QtCore.QLocale.China))
        self.chatHistoryTextEdit.setDocumentTitle(_fromUtf8(""))
        self.chatHistoryTextEdit.setReadOnly(True)
        self.chatHistoryTextEdit.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.chatHistoryTextEdit.setObjectName(_fromUtf8("chatHistoryTextEdit"))
        self.contactNameLabel = QtGui.QLabel(chatWindow)
        self.contactNameLabel.setGeometry(QtCore.QRect(150, 30, 271, 16))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.contactNameLabel.setFont(font)
        self.contactNameLabel.setObjectName(_fromUtf8("contactNameLabel"))
        self.portrait_label = QtGui.QLabel(chatWindow)
        self.portrait_label.setGeometry(QtCore.QRect(80, 10, 50, 50))
        self.portrait_label.setStyleSheet(_fromUtf8("border: 1px solid #ccc;"))
        self.portrait_label.setObjectName(_fromUtf8("portrait_label"))

        self.retranslateUi(chatWindow)
        self.convTab.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(chatWindow)

    def retranslateUi(self, chatWindow):
        chatWindow.setWindowTitle(QtGui.QApplication.translate("chatWindow", "Chat", None, QtGui.QApplication.UnicodeUTF8))
        self.convTab.setTabText(self.convTab.indexOf(self.tab), QtGui.QApplication.translate("chatWindow", "Tab 1", None, QtGui.QApplication.UnicodeUTF8))
        self.convTab.setTabText(self.convTab.indexOf(self.tab_2), QtGui.QApplication.translate("chatWindow", "Tab 2", None, QtGui.QApplication.UnicodeUTF8))
        self.contactNameLabel.setText(QtGui.QApplication.translate("chatWindow", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.portrait_label.setText(QtGui.QApplication.translate("chatWindow", "portrait", None, QtGui.QApplication.UnicodeUTF8))

