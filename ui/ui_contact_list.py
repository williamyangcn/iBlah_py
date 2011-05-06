# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/lee/backups/code/iblah_py/ui/ui_contact_list.ui'
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

class Ui_ContactListWindow(object):
    def setupUi(self, ContactListWindow):
        ContactListWindow.setObjectName(_fromUtf8("ContactListWindow"))
        ContactListWindow.resize(300, 500)
        ContactListWindow.setMinimumSize(QtCore.QSize(300, 500))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Lucida Grande"))
        font.setPointSize(12)
        ContactListWindow.setFont(font)
        self.presenceComboBox = QtGui.QComboBox(ContactListWindow)
        self.presenceComboBox.setGeometry(QtCore.QRect(30, 40, 100, 26))
        self.presenceComboBox.setObjectName(_fromUtf8("presenceComboBox"))
        self.nicknameLabel = QtGui.QLabel(ContactListWindow)
        self.nicknameLabel.setGeometry(QtCore.QRect(10, 20, 121, 16))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.nicknameLabel.setFont(font)
        self.nicknameLabel.setObjectName(_fromUtf8("nicknameLabel"))
        self.add_buddy_btn = QtGui.QToolButton(ContactListWindow)
        self.add_buddy_btn.setGeometry(QtCore.QRect(10, 450, 27, 23))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setWeight(75)
        font.setBold(True)
        self.add_buddy_btn.setFont(font)
        self.add_buddy_btn.setObjectName(_fromUtf8("add_buddy_btn"))
        self.reportBugBtn = QtGui.QToolButton(ContactListWindow)
        self.reportBugBtn.setGeometry(QtCore.QRect(190, 450, 91, 23))
        self.reportBugBtn.setObjectName(_fromUtf8("reportBugBtn"))
        self.presenceLabel = QtGui.QLabel(ContactListWindow)
        self.presenceLabel.setGeometry(QtCore.QRect(10, 45, 62, 16))
        self.presenceLabel.setObjectName(_fromUtf8("presenceLabel"))
        self.portraitLabel = QtGui.QLabel(ContactListWindow)
        self.portraitLabel.setGeometry(QtCore.QRect(230, 10, 60, 60))
        self.portraitLabel.setStyleSheet(_fromUtf8("border:2px solid #ccc;"))
        self.portraitLabel.setObjectName(_fromUtf8("portraitLabel"))
        self.contact_list_tree_view = QtGui.QTreeView(ContactListWindow)
        self.contact_list_tree_view.setGeometry(QtCore.QRect(10, 80, 280, 360))
        self.contact_list_tree_view.setDragEnabled(False)
        self.contact_list_tree_view.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        self.contact_list_tree_view.setAlternatingRowColors(True)
        self.contact_list_tree_view.setAutoExpandDelay(3)
        self.contact_list_tree_view.setIndentation(20)
        self.contact_list_tree_view.setUniformRowHeights(False)
        self.contact_list_tree_view.setSortingEnabled(True)
        self.contact_list_tree_view.setAnimated(True)
        self.contact_list_tree_view.setHeaderHidden(True)
        self.contact_list_tree_view.setObjectName(_fromUtf8("contact_list_tree_view"))

        self.retranslateUi(ContactListWindow)
        QtCore.QMetaObject.connectSlotsByName(ContactListWindow)

    def retranslateUi(self, ContactListWindow):
        ContactListWindow.setWindowTitle(QtGui.QApplication.translate("ContactListWindow", "Contacts", None, QtGui.QApplication.UnicodeUTF8))
        self.nicknameLabel.setText(QtGui.QApplication.translate("ContactListWindow", "nicknameLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.add_buddy_btn.setToolTip(QtGui.QApplication.translate("ContactListWindow", "添加好友", None, QtGui.QApplication.UnicodeUTF8))
        self.add_buddy_btn.setText(QtGui.QApplication.translate("ContactListWindow", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.add_buddy_btn.setShortcut(QtGui.QApplication.translate("ContactListWindow", "Ctrl+Shift+=", None, QtGui.QApplication.UnicodeUTF8))
        self.reportBugBtn.setText(QtGui.QApplication.translate("ContactListWindow", "提交 Bugs", None, QtGui.QApplication.UnicodeUTF8))
        self.reportBugBtn.setShortcut(QtGui.QApplication.translate("ContactListWindow", "Ctrl+Shift+R", None, QtGui.QApplication.UnicodeUTF8))
        self.presenceLabel.setText(QtGui.QApplication.translate("ContactListWindow", "presence", None, QtGui.QApplication.UnicodeUTF8))
        self.portraitLabel.setText(QtGui.QApplication.translate("ContactListWindow", "portrait", None, QtGui.QApplication.UnicodeUTF8))

