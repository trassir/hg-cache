#!/usr/bin/env python2

import os
import sys
import subprocess


def ENVVAR_HG_CACHE():
    return "HG_CACHE"


def IS_PYTEST():
    return "pytest" in sys.modules


def EXE_HG(sys_executable = sys.executable):
    hg_names = [os.path.sep + "hg.exe", os.path.sep + "hg"]
    hg_full_path = ""
    for hg_name in hg_names:
        if sys_executable.endswith(hg_name):
            hg_full_path = os.path.abspath(sys_executable)
    if hg_full_path:
        return hg_full_path
    for hg_name in hg_names:
        # importing pip is not supported by devs, they recommend this instead
        cmd = [sys_executable, "-m", "pip", "show", "-f", "mercurial"]
        mercurial_files = subprocess.check_output(cmd).splitlines()
        module_location = filter(lambda x: x.startswith("Location: "), mercurial_files)[0].split(": ")[1].strip()
        hg_paths = filter(lambda x, name=hg_name: x.endswith(name), mercurial_files)
        if hg_paths:
            hg_full_path = os.path.abspath(os.path.join(module_location, hg_paths[0].strip()))
            break
    return hg_full_path


def HG_PLUGIN_ARGS(use_self):
    if use_self:
        args = ["--config",
                "extensions.hgcache=%s" % os.path.dirname(__file__)]
    else:
        args = ["--config",
                "extensions.hgcache=!"]
    return args
