#!/usr/bin/env python2

import os
import sys


def ENVVAR_HG_CACHE():
    return "HG_CACHE"


def IS_PYTEST():
    return "pytest" in sys.modules


def EXE_HG():
    return "hg"


def HG_PLUGIN_ARGS(use_self):
    if use_self:
        args = ["--config",
                "extensions.hgcache=%s" % os.path.dirname(__file__)]
    else:
        args = ["--config",
                "extensions.hgcache=!"]
    return args
