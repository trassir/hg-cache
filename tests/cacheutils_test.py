import os
import shutil
import pytest
from hg_cache.constants import ENVVAR_HG_CACHE
from hg_cache.cacheutils import HgCacheConfigError
from hg_cache.cacheutils import HgCacheOperationError
from hg_cache.cacheutils import HgCacheInconsistentError
from hg_cache.cacheutils import initialize_cache
from hg_cache.hgutils import hg_config_set_default_remote
from hg_cache.hgutils import hg_spoil_extra_changeset
from hg_cache.hgutils import hg_spoil_local_changes


def test_initialize_cache_no_envvar():
    os.environ.pop(ENVVAR_HG_CACHE(), None)
    with pytest.raises(HgCacheConfigError):
        initialize_cache(None, None)


def test_initialize_cache_not_a_dir(tmpdir):
    f = tmpdir / "file.txt"
    f.write("the text")
    os.environ[ENVVAR_HG_CACHE()] = str(f)
    with pytest.raises(HgCacheConfigError):
        initialize_cache(None, None)


def test_initialize_cache_nonexistent(prepare_repos):
    (_, cache, remote, _) = prepare_repos
    os.environ[ENVVAR_HG_CACHE()] = \
        os.path.join(cache, "more", "directories", "to", "cache")
    cache_dir = initialize_cache(None, remote)
    assert cache_dir != ""


def test_initialize_cache_not_repo(prepare_repos):
    (_, _, remote, _) = prepare_repos
    shutil.rmtree(os.path.join(os.path.join(remote, ".hg")))
    os.environ[ENVVAR_HG_CACHE()] = remote
    with pytest.raises(HgCacheOperationError):
        initialize_cache(None, remote)


def test_initialize_cache_irrelevant_remote(prepare_repos):
    (_, cache, remote, foreign) = prepare_repos
    os.environ[ENVVAR_HG_CACHE()] = cache
    cache_dir = initialize_cache(None, remote)
    assert cache_dir == cache
    hg_config_set_default_remote(cache_dir, foreign)
    with pytest.raises(HgCacheInconsistentError):
        initialize_cache(None, remote)


def test_initialize_cache_extraslash(prepare_repos):
    (_, cache, remote, _) = prepare_repos
    os.environ[ENVVAR_HG_CACHE()] = cache
    cache_dir = initialize_cache(None, remote)
    assert cache_dir == cache
    hg_config_set_default_remote(cache_dir, remote + "/")
    initialize_cache(None, remote)


def test_initialize_cache_have_outgoing(prepare_repos):
    (_, cache, remote, _) = prepare_repos
    os.environ[ENVVAR_HG_CACHE()] = cache
    cache_dir = initialize_cache(None, remote)
    assert cache_dir == cache
    hg_config_set_default_remote(cache_dir, remote)
    hg_spoil_extra_changeset(cache_dir)
    os.environ[ENVVAR_HG_CACHE()] = cache
    with pytest.raises(HgCacheInconsistentError):
        initialize_cache(None, remote)


def test_initialize_cache_have_local_changes(prepare_repos):
    (_, cache, remote, _) = prepare_repos
    os.environ[ENVVAR_HG_CACHE()] = cache
    cache_dir = initialize_cache(None, remote)
    assert cache_dir == cache
    hg_config_set_default_remote(cache_dir, remote)
    hg_spoil_local_changes(cache_dir)
    os.environ[ENVVAR_HG_CACHE()] = cache
    with pytest.raises(HgCacheInconsistentError):
        cache_dir = initialize_cache(None, remote)
