#!/usr/bin/env python2

import os
import subprocess
import hashlib
from hgcache.constants import EXE_HG
from hgcache.exeutils import execute_in_subdir
from hgcache.exeutils import execute_hg_in_subdir
from hgcache.exeutils import execute_hg_in_subdir_or_die


def hg_create_randomrepo(root, ncommits):
    def _hg_commit(size):
        text = open(__file__).read()
        filedata = (text * (size / len(text) + 1))[:size]
        md5 = hashlib.md5()
        md5.update(filedata)
        filename = os.path.join(md5.hexdigest())
        open(filename, "wb").write(filedata)
        subprocess.check_call([EXE_HG(), "add", filename])
        subprocess.check_call([EXE_HG(), "commit", "-m", "add %s" % filename])
    cd = os.curdir
    os.chdir("%s" % root)
    subprocess.check_call([EXE_HG(), "init"])
    for i in xrange(1, ncommits):
        _hg_commit(128 * i)
    os.chdir(cd)


def hg_spoil_extra_changeset(repo):
    execute_in_subdir(repo, ["touch", "spoilfile"])
    execute_hg_in_subdir(repo, ["add", "spoilfile"])
    execute_hg_in_subdir(repo, ["ci", "-m", "spoilfile"])


def hg_spoil_missing_changeset(repo):
    rc, out = execute_hg_in_subdir(repo, ["id", "-n"])
    execute_hg_in_subdir(repo, ["strip", "-r", out])


def hg_spoil_local_changes(repo):
    with open(os.path.join(repo, "localchange"), "a") as f:
        f.write("localchange")
    execute_hg_in_subdir(repo, ["add", "localchange"])


def hg_config(directory, ui=None):
    rc, out = execute_hg_in_subdir_or_die(directory, ["config"], ui=ui)
    return dict(
        [[x[:x.index("=")], x[x.index("=")+1:]]
         for x in out.splitlines()])


def hg_config_set_default_remote(directory, remote):
    with open(os.path.join(directory, ".hg", "hgrc"), "a") as hgrc:
        hgrc.write("\n[paths]\n")
        hgrc.write("default={default}\n".format(default=remote))


def hg_log(local, ui=None, cache=None, use_self=False):
    return execute_hg_in_subdir_or_die(
        local, ["log"], ui=ui, cache=cache, use_self=use_self)


def hg_strip(local, revset, ui=None, cache=None, use_self=False):
    return execute_hg_in_subdir_or_die(
        local, ["strip", "-r", revset], ui=ui, cache=cache, use_self=use_self)


def hg_diff(local, ui=None, cache=None, use_self=False):
    return execute_hg_in_subdir_or_die(
        local, ["diff"], ui=ui, cache=cache, use_self=use_self)


def hg_clone(local, remote, ui=None, cache=None, use_self=False):
    return execute_hg_in_subdir_or_die(
        local, ["clone", remote, "."], ui=ui, cache=cache, use_self=use_self)


def hg_pull(local, remote, ui=None, cache=None, use_self=False):
    return execute_hg_in_subdir_or_die(
        local, ["pull", remote], ui=ui, cache=cache, use_self=use_self)


def hg_have_out(local, remote, ui=None, cache=None, use_self=False):
    return execute_hg_in_subdir_or_die(
        local, ["out", remote], ui=ui,
        good_retcodes=[0, 1], cache=cache, use_self=use_self)


def hg_have_in(local, remote, ui=None, cache=None, use_self=False):
    return execute_hg_in_subdir_or_die(
        local, ["in", remote], ui=ui,
        good_retcodes=[0, 1], cache=cache, use_self=use_self)
