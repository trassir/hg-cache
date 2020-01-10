#!/usr/bin/env python2

import pytest
from hgutils import hg_clone
from hgutils import hg_pull
from hgutils import hg_spoil_extra_changeset
from hgutils import hg_spoil_local_changes
from hgutils import hg_spoil_missing_changeset
from exeutils import execute_hg_in_subdir
from exeutils import SubcommandException


def _assert_repo_understood_by_hg(repo):
    rc, out = execute_hg_in_subdir(repo, ["log", "-G"])
    assert rc == 0, "repo history cannot be browsed"


def _assert_cache_consistent(local, cache):
    _assert_repo_understood_by_hg(local)
    _assert_repo_understood_by_hg(cache)
    rc, out = execute_hg_in_subdir(
        local, ["out", cache], cache=cache, use_self=True)
    assert rc == 1, "local repo have more commits than cache"
    rc, out = execute_hg_in_subdir(
        local, ["in", cache], cache=cache, use_self=True)
    assert rc == 1, "local repo have less commits than cache"


def _clean(repo):
    pass


def test_hgcache_fresh_clone_by_abspath(prepare_repos):
    (local, cache, remote, foreign) = prepare_repos
    _assert_repo_understood_by_hg(remote)
    rc, out = execute_hg_in_subdir(
        foreign, ["clone", remote, local], cache=cache, use_self=True)
    assert rc == 0
    _assert_cache_consistent(local, cache)


def test_hgcache_fresh_clone_by_curdir(prepare_repos):
    (local, cache, remote, foreign) = prepare_repos
    _assert_repo_understood_by_hg(remote)
    rc, out = execute_hg_in_subdir(
        local, ["clone", remote, "."], cache=cache, use_self=True)
    assert rc == 0
    _assert_cache_consistent(local, cache)


def test_hgcache_fresh_clone_by_omit(prepare_repos):
    (local, cache, remote, foreign) = prepare_repos
    _assert_repo_understood_by_hg(remote)
    rc, out = execute_hg_in_subdir(
        local, ["clone", remote], cache=cache, use_self=True)
    assert rc == 0
    subdir_name = remote.split("/")[-1]
    _assert_cache_consistent(local + "/" + subdir_name, cache)


@pytest.mark.parametrize("local_spoiler", [
    _clean,
    hg_spoil_extra_changeset,
    hg_spoil_missing_changeset,
    hg_spoil_local_changes
])
@pytest.mark.parametrize("cache_spoiler", [
    _clean,
    hg_spoil_missing_changeset
])
def test_hgcache_spoiled_pull_recover(
        prepare_repos, local_spoiler, cache_spoiler):
    (local, cache, remote, foreign) = prepare_repos
    # prepare typical situation of cache being used
    _assert_repo_understood_by_hg(remote)
    rc, out = hg_clone(cache, remote)
    assert rc == 0
    rc, out = hg_clone(local, remote)
    assert rc == 0
    # add typical modifications that could happen to repos during usage
    local_spoiler(local)
    cache_spoiler(cache)
    # ensure that plugin can recover from that
    rc, out = hg_pull(local, remote, cache=cache, use_self=True)
    assert rc == 0
    _assert_cache_consistent(local, cache)


@pytest.mark.parametrize("cache_spoiler", [
    hg_spoil_extra_changeset,
    hg_spoil_local_changes
])
def test_hgcache_spoiled_cache_fail(prepare_repos, cache_spoiler):
    (local, cache, remote, foreign) = prepare_repos
    # prepare typical situation of cache being used
    _assert_repo_understood_by_hg(remote)
    rc, out = hg_clone(cache, remote)
    assert rc == 0
    rc, out = hg_clone(local, remote)
    assert rc == 0
    # spoil cache to be unusable
    cache_spoiler(cache)
    # ensure that plugin refuses to work with it to avoid data loss
    with pytest.raises(SubcommandException) as excinfo:
        hg_pull(local, remote, cache=cache, use_self=True)
    assert excinfo.match("HgCacheInconsistentError")
