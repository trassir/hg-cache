import os
from .constants import ENVVAR_HG_CACHE
from .hgutils import hg_diff
from .hgutils import hg_pull
from .hgutils import hg_clone
from .hgutils import hg_have_out
from .hgutils import hg_config
from .logger import log


class HgCacheConfigError(RuntimeError):
    """When cache cannot be initialised using specified configuration"""


class HgCacheOperationError(RuntimeError):
    """When one of hg operations on cache fails"""


class HgCacheInconsistentError(RuntimeError):
    """When cache sync operation fails to avoid data loss"""


def initialize_cache(ui, remote: str):
    # cache dir must be specified
    if not ENVVAR_HG_CACHE() in os.environ:
        raise HgCacheConfigError(
            "environment variable {var} is not set".format(
                var=ENVVAR_HG_CACHE()))

    cache_dir = os.path.abspath(os.environ[ENVVAR_HG_CACHE()])

    # cache dir must exist
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    # cache dir must be a directory
    if not os.path.isdir(cache_dir):
        raise HgCacheConfigError(
            "cache directory '{cache_dir}' is not a directory".format(
                cache_dir=cache_dir))

    # empty cache should be initialized with clean clone of remote
    if os.listdir(cache_dir) == []:
        log("cache at {cache_dir} is empty, populate using clone of {remote}"
            .format(cache_dir=cache_dir, remote=remote), ui=ui)
        hg_clone(cache_dir, remote, ui=ui)

    # cache has to be configured to use requested remote
    cache_cfg = hg_config(cache_dir, ui=ui)
    if "paths.default" not in cache_cfg:
        raise HgCacheOperationError(
            "could not read default path for cache at {cache}".format(
                cache=cache_dir))
    cache_path_default = cache_cfg["paths.default"]
    cache_path_default_cmp = cache_path_default.lower().replace("\\", "/").rstrip("/")
    remote_cmp = remote.lower().replace("\\", "/").rstrip("/")
    if cache_path_default_cmp != remote_cmp:
        raise HgCacheInconsistentError(
            "cache in {cache_dir} is from irrelevant repo '{foreign}'"
            " - expected '{remote}'".format(
                foreign=cache_path_default,
                remote=remote,
                cache_dir=cache_dir))

    # cache must never have outgoing changesets
    rc, out = hg_have_out(cache_dir, remote, ui=ui)
    if rc == 0:
        raise HgCacheInconsistentError(
            "cache at {cache} have outgoing commits to {remote}:\n{commits}"
            .format(cache=cache_dir, remote=remote, commits=out))

    # cache must never have outgoing changesets
    rc, out = hg_diff(cache_dir, ui=ui)
    if rc != 0:
        raise HgCacheOperationError(
            "could not read hg diff from cache at cache at {cache}".format(
                cache=cache_dir))  # pragma: no cover
    if out:
        raise HgCacheInconsistentError(
            "cache at {cache} have local changes:\n{commits}".format(
                cache=cache_dir, commits=out))

    # cache must be fresh
    rc, out = hg_pull(cache_dir, remote, ui=ui)
    if rc != 0:
        raise HgCacheOperationError(
            "cache at {cache} could not pull from {remote}:\n{out}".format(
                cache=cache_dir, remote=remote, out=out))  # pragma: no cover

    return os.path.abspath(cache_dir).replace("\\", "/")
