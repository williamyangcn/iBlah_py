import sys

from PyQt4 import QtCore
from libblah.consts import get_platform
from libblah.log import logger


def get_python_version():
    return sys.version.split(' ')[0]

def get_qt_version():
    return QtCore.qVersion()

def check_runtime():
    pl = get_platform()
    logger.info('Platform: %s' % pl)
    logger.info("Python Version: %s" % get_python_version())
    logger.info("Qt4 Version: %s" % get_qt_version())

    # required Mac or Linux
    if pl not in ("Darwin", "Linux"):
        logger.error("Blah only supports Mac OS X and Linux")
        sys.exit(-1)

    # required >= Python-2.6
    ver = sys.version_info[1]
    if ver < 6:
        logger.error("Blah requires >=Python-2.6, found %s" % get_python_version())
        sys.exit(-1)

    qt_vers = [int(i) for i in get_qt_version().split('.')]
    # required >= Qt-4.6
    if qt_vers[1] < 6:
        logger.error("Blah requires >=Qt-4.6, found %s" % get_qt_version())
        sys.exit(-1)