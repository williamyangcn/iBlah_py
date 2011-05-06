# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/lee/backups/code/iblah_py/ui/ui_exit_tips_dialog.ui'
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

class Ui_ExitTipsDialog(object):
    def setupUi(self, ExitTipsDialog):
        ExitTipsDialog.setObjectName(_fromUtf8("ExitTipsDialog"))
        ExitTipsDialog.resize(320, 240)
        ExitTipsDialog.setModal(True)
        self.buttonBox = QtGui.QDialogButtonBox(ExitTipsDialog)
        self.buttonBox.setGeometry(QtCore.QRect(10, 200, 301, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.minimizeRadioButton = QtGui.QRadioButton(ExitTipsDialog)
        self.minimizeRadioButton.setGeometry(QtCore.QRect(30, 70, 271, 20))
        self.minimizeRadioButton.setObjectName(_fromUtf8("minimizeRadioButton"))
        self.exitRadioButton = QtGui.QRadioButton(ExitTipsDialog)
        self.exitRadioButton.setGeometry(QtCore.QRect(30, 100, 102, 20))
        self.exitRadioButton.setChecked(True)
        self.exitRadioButton.setObjectName(_fromUtf8("exitRadioButton"))
        self.label = QtGui.QLabel(ExitTipsDialog)
        self.label.setGeometry(QtCore.QRect(20, 30, 281, 31))
        self.label.setObjectName(_fromUtf8("label"))
        self.confirmCheckBox = QtGui.QCheckBox(ExitTipsDialog)
        self.confirmCheckBox.setGeometry(QtCore.QRect(150, 150, 151, 20))
        self.confirmCheckBox.setObjectName(_fromUtf8("confirmCheckBox"))

        self.retranslateUi(ExitTipsDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ExitTipsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ExitTipsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ExitTipsDialog)

    def retranslateUi(self, ExitTipsDialog):
        ExitTipsDialog.setWindowTitle(QtGui.QApplication.translate("ExitTipsDialog", "Tips", None, QtGui.QApplication.UnicodeUTF8))
        self.minimizeRadioButton.setText(QtGui.QApplication.translate("ExitTipsDialog", "Minimize to system tray withou exiting", None, QtGui.QApplication.UnicodeUTF8))
        self.exitRadioButton.setText(QtGui.QApplication.translate("ExitTipsDialog", "Exit program", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ExitTipsDialog", "When you click the close button should me:", None, QtGui.QApplication.UnicodeUTF8))
        self.confirmCheckBox.setText(QtGui.QApplication.translate("ExitTipsDialog", "Don\'t ask me again", None, QtGui.QApplication.UnicodeUTF8))

