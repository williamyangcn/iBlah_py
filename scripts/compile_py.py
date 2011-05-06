#!/usr/bin/env python
import os
import compileall
osp = os.path

PWD = osp.dirname(osp.realpath(__file__))

compileall.compile_dir(osp.join(osp.dirname(PWD)))