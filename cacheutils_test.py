import os
import shutil
import pytest
from constants import ENVVAR_HG_CACHE
from cacheutils import HgCacheConfigError
from cacheutils import HgCacheOperationError
from cacheutils import HgCacheInconsistentError
from cacheutils import initialize_cache
from hgutils import hg_config_set_default_remote
from hgutils import hg_spoil_extra_changeset
from hgutils import hg_spoil_local_changes


def test_initialize_cache_no_envvar():
    os.environ.pop(ENVVAR_HG_CACHE(), None)
    with pytest.raises(HgCacheConfigError):
        initialize_cache(None, None)


def test_initialize_cache_not_a_dir(tmpdir, prepare_repos):
    (_, _, _, remote, _) = prepare_repos
    f = tmpdir / "file.txt"
    f.write("the text")
    os.environ[ENVVAR_HG_CACHE()] = str(f)
    with pytest.raises(HgCacheConfigError):
        initialize_cache(None, remote)


def test_initialize_cache_nonexistent(prepare_repos):
    (_, cache_root, _, remote, _) = prepare_repos
    os.environ[ENVVAR_HG_CACHE()] = \
        os.path.join(cache_root, "more", "directories", "to", "cache")
    cache_dir = initialize_cache(None, remote)
    assert cache_dir != ""


def test_initialize_cache_not_repo(prepare_repos):
    (_, cache_root, cache_specific, remote, _) = prepare_repos
    os.environ[ENVVAR_HG_CACHE()] = cache_root
    initialize_cache(None, remote)
    shutil.rmtree(os.path.join(os.path.join(cache_specific, ".hg")))
    with pytest.raises(HgCacheOperationError):
        initialize_cache(None, remote)


def test_initialize_cache_irrelevant_remote(prepare_repos):
    (_, cache_root, cache_specific, remote, foreign) = prepare_repos
    os.environ[ENVVAR_HG_CACHE()] = cache_root
    cache_dir = initialize_cache(None, remote)
    assert cache_dir == cache_specific
    hg_config_set_default_remote(cache_dir, foreign)
    with pytest.raises(HgCacheInconsistentError):
        initialize_cache(None, remote)


def test_initialize_cache_have_outgoing(prepare_repos):
    (_, cache_root, cache_specific, remote, _) = prepare_repos
    os.environ[ENVVAR_HG_CACHE()] = cache_root
    cache_dir = initialize_cache(None, remote)
    assert cache_dir == cache_specific
    hg_config_set_default_remote(cache_dir, remote)
    hg_spoil_extra_changeset(cache_dir)
    os.environ[ENVVAR_HG_CACHE()] = cache_root
    with pytest.raises(HgCacheInconsistentError):
        initialize_cache(None, remote)


def test_initialize_cache_have_local_changes(prepare_repos):
    (_, cache_root, cache_specific, remote, _) = prepare_repos
    os.environ[ENVVAR_HG_CACHE()] = cache_root
    cache_dir = initialize_cache(None, remote)
    assert cache_dir == cache_specific
    hg_config_set_default_remote(cache_dir, remote)
    hg_spoil_local_changes(cache_dir)
    os.environ[ENVVAR_HG_CACHE()] = cache_root
    with pytest.raises(HgCacheInconsistentError):
        cache_dir = initialize_cache(None, remote)
