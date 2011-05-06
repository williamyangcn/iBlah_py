import os
from PyQt4 import QtGui
from libblah.consts import get_platform

def get_best_font():
    pl = get_platform()
    IS_GNOME = os.getenv("GDMSESSION") and os.getenv("GDMSESSION") == "gnome"

    font = None
    if pl == "Linux" and IS_GNOME:
        font = QtGui.QFont("WenQuanYi Zen Hei", 12) # DejaVu Sans
    return font

def set_font(widget, font):
    if font:
        widget.setFont(font)