#!/usr/bin/env python2

import os
import subprocess
from hgcache.logger import log
from hgcache.constants import ENVVAR_HG_CACHE
from hgcache.constants import HG_PLUGIN_ARGS
from hgcache.constants import IS_PYTEST
from hgcache.constants import EXE_HG


class SubcommandException(RuntimeError):
    """Raise when running subcommand was not successful"""

    def __init__(self, retcode, subdir, cmd, output):
        RuntimeError.__init__(self)
        self.retcode = retcode
        self.subdir = subdir
        self.cmd = cmd
        self.output = output

    def __str__(self):
        return "\nEXIT={rc}\nDIR={d}\nCMD={cmd}\n{out}".format(
            rc=self.retcode, d=self.subdir, cmd=self.cmd, out=self.output)


def execute_in_subdir(subdir, args, cache="", ui=None):
    cd = os.path.abspath(os.curdir)
    os.chdir("%s" % subdir)
    rc = 0
    out = ""
    try:
        if cache is not None:
            os.environ[ENVVAR_HG_CACHE()] = "%s" % cache
        out = subprocess.check_output(args, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
        rc = e.returncode
        out = e.output
    os.chdir(cd)
    if IS_PYTEST():
        log("[ {rc} ] : {subdir} : {args}".format(
            rc=rc, subdir=os.path.abspath("%s" % subdir), args=args),
            ui=ui)
    return rc, out


def execute_hg_in_subdir(subdir, args, cache="", ui=None, use_self=False):
    return execute_in_subdir(
        subdir, [EXE_HG()] + args + HG_PLUGIN_ARGS(use_self), cache=cache,
        ui=ui)


def execute_hg_in_subdir_or_die(
        subdir, args, cache=None, ui=None, use_self=False, good_retcodes=None):
    if good_retcodes is None:
        good_retcodes = [0]
    cmd = [EXE_HG()] + args + HG_PLUGIN_ARGS(use_self)
    rc, out = execute_in_subdir(subdir, cmd, cache=cache, ui=ui)
    if rc not in good_retcodes:
        raise SubcommandException(rc, os.path.abspath("%s" % subdir), cmd, out)
    return rc, out
