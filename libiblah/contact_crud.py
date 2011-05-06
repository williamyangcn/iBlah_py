from PyQt4 import QtGui
from PyQt4 import QtCore
from libblah.strutils import to_unicode_obj
from libblah.utils import qstr_to_unicode_obj

from ui.ui_add_buddy_dialog import Ui_AddBuddyDialog
from ui.ui_reply_add_buddy_dialog import Ui_ReplyAddBuddyDialog
from ui.ui_delete_buddy_dialog import Ui_DeleteBuddyDialog


class AddBuddyDialog(QtGui.QDialog, Ui_AddBuddyDialog):
    def __init__(self, parent = None, name = ""):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.account_line_edit = self.AccountLineEdit
        self.name_line_edit = self.NameLineEdit
        self.msg_combo_box = self.MsgComboBox

        self.name_line_edit.setText(to_unicode_obj(name))

    def get_return(self):
        account = str(self.account_line_edit.text().toUtf8())
        name = qstr_to_unicode_obj(self.name_line_edit.text())
        data = {
            "account" : account,
            "name" : name,
            "add_buddy_phrases" : self.msg_combo_box.currentIndex(),
        }
        return data

    @staticmethod
    def get_data(parent, name = ""):
        dlg = AddBuddyDialog(parent, name)
        dlg.show()

        result = dlg.exec_()
        if result == QtGui.QDialog.Accepted:
            btn_val = True
        else:
            btn_val = False
        return (btn_val, dlg.get_return())


class ReplyAddBuddyDialog(QtGui.QDialog, Ui_ReplyAddBuddyDialog):
    def __init__(self, parent, show_msg):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.msg_text_edit.setText(show_msg)
        self.refuse_radio_btn.toggled.connect(self.on_refuse_radio_btn_change)
        self.accept_radio_btn.toggled.connect(self.on_accept_radio_btn_change)

    def on_refuse_radio_btn_change(self, checked):
        if checked:
            self.decline_add_req_check_box.setEnabled(True)
            self.reason_line_edit.setEnabled(True)
        else:
            self.decline_add_req_check_box.setEnabled(False)
            self.reason_line_edit.setEnabled(False)

        self.send_btn.setEnabled(True)

    def on_accept_radio_btn_change(self, checked):
        assert checked != None
        self.send_btn.setEnabled(True)

    def get_return(self):
        data = {
            "accept" : self.accept_radio_btn.isChecked(),
            "decline_add_req_forever" : self.decline_add_req_check_box.isChecked(),
            "refuse_reason" : qstr_to_unicode_obj(self.reason_line_edit.text()),
        }
        return data

    @staticmethod
    def get_data(parent, show_msg):
        dlg = ReplyAddBuddyDialog(parent, show_msg)
        dlg.show()

        result = dlg.exec_()
        if result == QtGui.QDialog.Accepted:
            btn_val = True
        else:
            btn_val = False
        return (btn_val, dlg.get_return())



class DeleteBuddyDialog(QtGui.QDialog, Ui_DeleteBuddyDialog):
    def __init__(self, parent, show_msg):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.show_msg_text_edit.setText(show_msg)
        self.delete_me_checkbox.stateChanged.connect(self.on_delete_me_changed)

    def on_delete_me_changed(self, checked):
        if checked == QtCore.Qt.Checked:
            self.no_btn.setEnabled(False)
        else:
            self.no_btn.setEnabled(True)

    def get_return(self):
        if self.delete_me_checkbox.isChecked():
            delete_both = True
        else:
            delete_both = False
        data = {
            "delete_both" : delete_both,
        }
        return data

    @staticmethod
    def get_data(parent, show_msg):
        dlg = DeleteBuddyDialog(parent, show_msg)
        dlg.show()

        result = dlg.exec_()
        if result == QtGui.QDialog.Accepted:
            btn_val = True
        else:
            btn_val = False
        return (btn_val, dlg.get_return())