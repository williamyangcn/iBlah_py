# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/lee/backups/code/iblah_py/ui/ui_verification_dialog.ui'
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

class Ui_VerificationDialog(object):
    def setupUi(self, VerificationDialog):
        VerificationDialog.setObjectName(_fromUtf8("VerificationDialog"))
        VerificationDialog.resize(400, 300)
        VerificationDialog.setModal(True)
        self.lineEdit = QtGui.QLineEdit(VerificationDialog)
        self.lineEdit.setGeometry(QtCore.QRect(180, 170, 144, 22))
        self.lineEdit.setText(_fromUtf8(""))
        self.lineEdit.setMaxLength(4)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.pushButton = QtGui.QPushButton(VerificationDialog)
        self.pushButton.setGeometry(QtCore.QRect(270, 240, 114, 32))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayoutWidget = QtGui.QWidget(VerificationDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(60, 20, 301, 121))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        self.label.setWordWrap(False)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(VerificationDialog)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("pressed()")), VerificationDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(VerificationDialog)

    def retranslateUi(self, VerificationDialog):
        VerificationDialog.setWindowTitle(QtGui.QApplication.translate("VerificationDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("VerificationDialog", "发送 (&S)", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("VerificationDialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))

