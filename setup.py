import os
from setuptools import setup, find_packages
import shutil
import sys
import glob
from libblah import consts


osp = os.path
PWD = osp.dirname(osp.realpath(__file__))

APP_NAME = consts.NAME
MAIN_APP_NAME = '%s.py' % APP_NAME
RES_PATH = os.path.join(PWD, 'dist', '%s.app' % APP_NAME, 'Contents', 'Resources')

data_files = [
        ("icons", glob.glob(osp.join(PWD, "icons", "*"))),
        ("scripts", glob.glob(osp.join(PWD, "scripts", "*"))),
        ("resource", glob.glob(osp.join(PWD, "resource", "*.nib"))),
        #('/usr/share/applications',['iBlah.desktop']),
    ]

packages = find_packages()

plist = dict(
    CFBundleName = APP_NAME,
    CFBundleShortVersionString = consts.version,
    CFBundleGetInfoString = ' '.join([APP_NAME, consts.version]),
    CFBundleExecutable = APP_NAME,
    CFBundleIdentifier = 'org.shuge.fetion',
)


def delete_old():
    BUILD_PATH = os.path.join(PWD, "build")
    DIST_PATH = os.path.join(PWD, "dist")
    if os.path.exists(BUILD_PATH):
         shutil.rmtree(BUILD_PATH)
    if os.path.exists(DIST_PATH):
        shutil.rmtree(DIST_PATH)

def create_app():
    apps = [
        {
            "script" : MAIN_APP_NAME,
            "plist" : plist,
        }
    ]
    OPTIONS = {'includes': ['sip', 'PyQt4.QtCore', 'PyQt4.QtGui']}

    setup(
        name = APP_NAME,
        version = consts.version,
        description = consts.DESCRIPTION_EN,
        author = consts.AUTHOR,
        author_email = consts.AUTHOR_EMAIL,
        platforms = ["Mac OSX"],
        license = "Shuge Property License",
        url = "http://bitbucket.org/shugelee/iblah/",
        scripts = [MAIN_APP_NAME],

        app = apps,
        options = {'py2app': OPTIONS},
        # setup_requires = ['py2app'],
        data_files = data_files,
        packages = packages,
    )

def qt_menu_patch():
    src = osp.join(PWD, 'resource', 'qt_menu.nib')
    dst = os.path.join(RES_PATH, 'qt_menu.nib')
    if not os.path.exists(dst):
        shutil.copytree(src, dst)

_RUN_IN_TERM_PATCH = """import os
import sys
osp = os.path
os.environ['RESOURCEPATH'] = osp.dirname(osp.realpath(__file__))

"""

#paths = []
#for i in sys.path:
#    if not i.startswith("/opt/") or not i.startswith("/sw/"):
#        paths.append(i)
#sys.path = paths
#from pprint import pprint as pp
#pp(sys.path)


# TODO: fix error about /opt/local/lib/libQtGui.4.dylib
# sys.path.remove(i) for i in sys.path if i.startswith("/opt")

def run_in_term_patch():
    BOOT_FILE_PATH = osp.join(RES_PATH, "__boot__.py")
    with open(BOOT_FILE_PATH) as f:
        old = f.read()

    new = _RUN_IN_TERM_PATCH + old

    with open(BOOT_FILE_PATH, 'w') as f:
        f.write(new)

def data_files_patch():
    for item in data_files:
        if isinstance(item, tuple):
            folder_name = item[0]
        else:
            folder_name = item

        src = osp.join(PWD, folder_name)
        dst = os.path.join(RES_PATH, folder_name)
        if not os.path.exists(dst):
            shutil.copytree(src, dst)

        
ACTION_CREATE = len(sys.argv) == 3 and sys.argv[-1] == "build"

if ACTION_CREATE:
    delete_old()
    create_app()
    qt_menu_patch()
    run_in_term_patch()
    data_files_patch()
else:
    create_app()
#     print "Usage: python setup.py py2app build"


