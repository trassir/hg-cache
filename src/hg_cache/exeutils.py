import os
import subprocess
from .logger import log
from .constants import ENVVAR_HG_CACHE
from .constants import HG_PLUGIN_ARGS
from .constants import IS_PYTEST
from .constants import EXE_HG


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
    out: bytes = b""
    try:
        if cache is not None:
            os.environ[ENVVAR_HG_CACHE()] = "%s" % cache
        out = subprocess.check_output(args, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        rc = e.returncode
        out = e.output

    os.chdir(cd)
    if IS_PYTEST():
        log("[ {rc} ] : {subdir} : {args}".format(
            rc=rc, subdir=os.path.abspath("%s" % subdir), args=args),
            ui=ui)
    return rc, out


def execute_hg_in_subdir(subdir, args, cache="", ui=None, use_self=False):
    rc, out = execute_in_subdir(
        subdir, [EXE_HG()] + args + HG_PLUGIN_ARGS(use_self), cache=cache,
        ui=ui)
    # if `uisetup(_)` fails in extension, then mercurial prints traceback,
    # but executes the underlying command without any wrapping done
    false_positives = [
        b'failed to import extension',
        b'failed to set up extension',
        b'Unknown exception encountered',
    ]
    if rc == 0 and any(x in out for x in false_positives):
        rc = -1
    return rc, out


def execute_hg_in_subdir_or_die(  #pylint: disable-msg=too-many-arguments
        subdir, args, cache=None, ui=None, use_self=False, good_retcodes=None):
    if good_retcodes is None:
        good_retcodes = [0]
    rc, out = execute_hg_in_subdir(subdir, args, cache=cache, ui=ui, use_self=use_self)
    if rc not in good_retcodes:
        raise SubcommandException(rc, os.path.abspath("%s" % subdir), args, out)
    return rc, out
