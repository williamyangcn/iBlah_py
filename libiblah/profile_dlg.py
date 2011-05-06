from PyQt4 import QtCore
from PyQt4 import QtGui
from ui.ui_profile_dialog import Ui_ProfileDialog
from libiblah.const import DEFAULT_PORTRAIT_PATH


class ProfileDialog(QtGui.QDialog, Ui_ProfileDialog):
    def __init__(self, parent = None, user = None, ready_only = True):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self._user = user
        self._ready_only = ready_only

        path = user.get_portrait_path() or DEFAULT_PORTRAIT_PATH
        self._avatar_pixmap = QtGui.QPixmap(path)
        width, height = 130, 130
        self._avatar_pixmap = self._avatar_pixmap.scaled(QtCore.QSize(width, height))
        self.avatar_label.setPixmap(self._avatar_pixmap)

        self.set_data(self._user, self._ready_only)

    def set_data(self, user, ready_only):
        self._user = user
        self._ready_only = ready_only

        self.fetion_no_line_edit.setText(self._user.sid)
        self.cellphone_no_line_edit.setText(self._user.mobile_no or "")
        self.email_line_edit.setText(self._user.get_email())
        self.fullname_line_edit.setText(self._user.get_name())
        self.impresa_text_edit.setText(self._user.impresa or "")

        portrait_path = self._user.get_portrait_path() or DEFAULT_PORTRAIT_PATH
        self.set_avatar(portrait_path)

        if self._ready_only:
            self.fetion_no_line_edit.setReadOnly(True)
            self.cellphone_no_line_edit.setReadOnly(True)
            self.email_line_edit.setReadOnly(True)
            self.fullname_line_edit.setReadOnly(True)
            self.impresa_text_edit.setReadOnly(True)

            self.save_btn.setEnabled(False)
            self.save_btn.hide()
        else:
            self.fetion_no_line_edit.setReadOnly(True)
            self.cellphone_no_line_edit.setReadOnly(True)
            self.email_line_edit.setReadOnly(True)

            self.save_btn.setEnabled(True)
            self.save_btn.show()

    def set_avatar(self, pic_path):
        self._avatar_pixmap.load(pic_path)

    def get_return(self):
        return self._user

    @staticmethod
    def get_data(parent, user = None, ready_only = True):
        dlg = ProfileDialog(parent, user, ready_only)
        dlg.show()

        result = dlg.exec_()
        if result == QtGui.QDialog.Accepted:
            btn_val = True
        else:
            btn_val = False
        return (btn_val, dlg.get_return())

