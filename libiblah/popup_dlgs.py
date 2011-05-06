#coding:utf-8
from PyQt4 import QtGui
#from PyQt4 import QtCore

from libblah.consts import ABOUT_MSG, ABOUT_TITLE

from ui.ui_verification_dialog import Ui_VerificationDialog

def popup_confirm(parent, msg = None):
    reply = QtGui.QMessageBox.question(parent, u"提示",
                 msg,
                 QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
    if reply == QtGui.QMessageBox.Yes:
        return True
    else:
        return False

def popup_warning(parent, msg = None):
    QtGui.QMessageBox.warning(parent, u"警告", msg, QtGui.QMessageBox.Close)

def popup_error(parent, msg = None):
    QtGui.QMessageBox.critical(parent, u"错误", msg, QtGui.QMessageBox.Close)

def popup_about(parent):
    QtGui.QMessageBox.about(parent, ABOUT_TITLE, ABOUT_MSG)


class GetInputDialog(QtGui.QDialog, Ui_VerificationDialog):
    def __init__(self, body = "Input: "):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.label.setText(body)


class GetVerificationDialog(GetInputDialog):
    def __init__(self, body, path):
        GetInputDialog.__init__(self, body)

        pix = QtGui.QPixmap(path)
        lab = QtGui.QLabel("verification", self)
        lab.setPixmap(pix)
        self.verticalLayout.addWidget(lab)

    @staticmethod
    def get_input(body = "Recognise and Input 4 characters: ", path = None):
        dlg = GetVerificationDialog(body, path)
        dlg.show()
        result = dlg.exec_()

        if result == QtGui.QDialog.Accepted:
            btn_val = True
        else:
            btn_val = False

        return (btn_val, str(dlg.lineEdit.text()))

