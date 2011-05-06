#!/usr/bin/env python
import os

osp = os.path
PWD = osp.dirname(osp.realpath(__file__))

qrcs = [osp.join(PWD, i) for i in os.listdir(PWD) if i.endswith(".qrc")]
for src in qrcs:
    dst = "%s_rcc.py" % osp.splitext(osp.basename(src))[0]
    dst = osp.join(osp.dirname(PWD), "libiblah", dst)
    cmd = '''pyrcc4-2.7 "%s" -o "%s"''' % (src, dst)
    os.system(cmd)