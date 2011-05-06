#!/usr/bin/env python
import os
from os import path as osp
from PyQt4.uic import compileUiDir
    
PWD = osp.dirname(os.path.realpath(__file__))
ui_path = osp.join(osp.dirname(PWD), "ui")

#def convert_py_filename(ui_dir, ui_filename):
#    ''' convert name, foo.ui -> ui_foo.py '''
#    py_filename = "ui_%s.py" % ui_filename[:-3]
#    return ui_dir, py_filename

compileUiDir(ui_path)


