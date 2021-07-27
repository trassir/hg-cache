import pytest
from hg_cache.hgutils import hg_clone
from hg_cache.hgutils import hg_pull
from hg_cache.hgutils import hg_spoil_extra_changeset
from hg_cache.hgutils import hg_spoil_local_changes
from hg_cache.hgutils import hg_spoil_missing_changeset
from hg_cache.exeutils import execute_hg_in_subdir
from hg_cache.exeutils import SubcommandException


def _assert_cache_consistent(local, cache):
    rc, out1 = execute_hg_in_subdir(local,
        ["log", "-T", "{node}\n"])
    assert rc == 0, "local repo history cannot be browsed"
    rc, out2 = execute_hg_in_subdir(cache,
        ["log", "-T", "{node}\n"])
    assert rc == 0, "cache repo history cannot be browsed"
    assert out1 == out2, "commits in cache and local do not match"


def _clean(repo):
    pass


def test__fresh__clone_by_abspath(prepare_repos):
    (local, cache, remote, _) = prepare_repos
    rc, out = execute_hg_in_subdir(
        '.', ["clone", remote, local], cache=cache, use_self=True)
    assert rc == 0, "clone should have succeeded; instead got:\n{}".format(out.decode())
    _assert_cache_consistent(local, cache)


def test__fresh__clone_by_curdir(prepare_repos):
    (local, cache, remote, _) = prepare_repos
    rc, out = execute_hg_in_subdir(
        local, ["clone", remote, "."], cache=cache, use_self=True)
    assert rc == 0, "clone should have succeeded; instead got:\n{}".format(out.decode())
    _assert_cache_consistent(local, cache)


def test__fresh__clone_by_omit(prepare_repos):
    (local, cache, remote, _) = prepare_repos
    rc, out = execute_hg_in_subdir(
        local, ["clone", remote], cache=cache, use_self=True)
    assert rc == 0, "clone should have succeeded; instead got:\n{}".format(out.decode())
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
def test__spoiled__pull_recover(
        prepare_repos, local_spoiler, cache_spoiler):
    (local, cache, remote, _) = prepare_repos
    # prepare typical situation of cache being used
    rc, out = hg_clone(local, remote, cache=cache, use_self=True)
    assert rc == 0, "clone should have succeeded; instead got:\n{}".format(out.decode())
    # add typical modifications that could happen to repos during usage
    local_spoiler(local)
    cache_spoiler(cache)
    # ensure that plugin can recover from that
    rc, out = hg_pull(local, remote, cache=cache, use_self=True)
    assert rc == 0, "pull should have succeeded; instead got:\n{}".format(out.decode())
    _assert_cache_consistent(local, cache)


@pytest.mark.parametrize("cache_spoiler", [
    hg_spoil_extra_changeset,
    hg_spoil_local_changes
])
def test__spoiled__cache_fail(prepare_repos, cache_spoiler):
    (local, cache, remote, _) = prepare_repos
    # prepare typical situation of cache being used
    rc, out = hg_clone(local, remote, cache=cache, use_self=True)
    assert rc == 0, "clone should have succeeded; instead got:\n{}".format(out.decode())
    # spoil cache to be unusable
    cache_spoiler(cache)
    # ensure that plugin refuses to work with it to avoid data loss
    with pytest.raises(SubcommandException) as excinfo:
        hg_pull(local, remote, cache=cache, use_self=True)
    assert excinfo.match("HgCacheInconsistentError")
