import os
from mercurial import extensions, commands
from .cacheutils import HgCacheOperationError
from .cacheutils import initialize_cache
from .hgutils import hg_config
from .hgutils import hg_strip
from .hgutils import hg_have_out
from .hgutils import hg_config_set_default_remote
from .logger import log


def _clone_with_cache(orig, ui, repo, *args, **opts):  # pragma: no cover
    cache_dir = initialize_cache(ui, repo)
    log("cloning using cache at {cdir}".format(cdir=cache_dir), ui=ui)
    target_dir = repo.split("/")[-1]
    if args:
        target_dir = args[0]
    args = (target_dir,) + args[1:]
    ret = orig(ui, cache_dir, *args, **opts)
    hg_config_set_default_remote(target_dir, repo)
    return ret


def _pull_with_cache(orig, ui, repo, *args, **opts):  # pragma: no cover
    remote = hg_config(".")["paths.default"]
    cache_dir = initialize_cache(ui, remote)
    log("pulling using cache at {cdir}".format(cdir=cache_dir), ui=ui)
    rc, out = hg_have_out(".", cache_dir, ui=ui)
    if rc != 1:
        rc, out = hg_strip(".", "outgoing('%s')" % cache_dir, ui=ui)
        if rc != 0:
            raise HgCacheOperationError(
                "repo at {d} could not strip outgoing to {r}:\n{o}".format(
                    d=os.path.abspath("."), r=cache_dir, o=out))
    args = (cache_dir,) + args[1:]
    return orig(ui, repo, *args, **opts)


def uisetup(_):  # pragma: no cover
    extensions.wrapcommand(commands.table, "clone", _clone_with_cache)
    extensions.wrapcommand(commands.table, "pull", _pull_with_cache)
