import os
import shutil
import pytest
from hgcache.constants import ENVVAR_HG_CACHE
from hgcache.cacheutils import HgCacheConfigError
from hgcache.cacheutils import HgCacheOperationError
from hgcache.cacheutils import HgCacheInconsistentError
from hgcache.cacheutils import initialize_cache
from hgcache.hgutils import hg_config_set_default_remote
from hgcache.hgutils import hg_spoil_extra_changeset
from hgcache.hgutils import hg_spoil_local_changes


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
    (local, cache, remote, foreign) = prepare_repos
    os.environ[ENVVAR_HG_CACHE()] = \
        os.path.join(cache, "more", "directories", "to", "cache")
    cache_dir = initialize_cache(None, remote)
    assert cache_dir != ""


def test_initialize_cache_not_repo(prepare_repos):
    (local, cache, remote, foreign) = prepare_repos
    shutil.rmtree(os.path.join(os.path.join(remote, ".hg")))
    os.environ[ENVVAR_HG_CACHE()] = remote
    with pytest.raises(HgCacheOperationError):
        initialize_cache(None, remote)


def test_initialize_cache_irrelevant_remote(prepare_repos):
    (local, cache, remote, foreign) = prepare_repos
    os.environ[ENVVAR_HG_CACHE()] = cache
    cache_dir = initialize_cache(None, remote)
    assert cache_dir == cache
    hg_config_set_default_remote(cache_dir, foreign)
    with pytest.raises(HgCacheInconsistentError):
        initialize_cache(None, remote)


def test_initialize_cache_have_outgoing(prepare_repos):
    (local, cache, remote, foreign) = prepare_repos
    os.environ[ENVVAR_HG_CACHE()] = cache
    cache_dir = initialize_cache(None, remote)
    assert cache_dir == cache
    hg_config_set_default_remote(cache_dir, remote)
    hg_spoil_extra_changeset(cache_dir)
    os.environ[ENVVAR_HG_CACHE()] = cache
    with pytest.raises(HgCacheInconsistentError):
        initialize_cache(None, remote)


def test_initialize_cache_have_local_changes(prepare_repos):
    (local, cache, remote, foreign) = prepare_repos
    os.environ[ENVVAR_HG_CACHE()] = cache
    cache_dir = initialize_cache(None, remote)
    assert cache_dir == cache
    hg_config_set_default_remote(cache_dir, remote)
    hg_spoil_local_changes(cache_dir)
    os.environ[ENVVAR_HG_CACHE()] = cache
    with pytest.raises(HgCacheInconsistentError):
        cache_dir = initialize_cache(None, remote)
