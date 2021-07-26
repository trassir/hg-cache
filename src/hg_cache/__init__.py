import os
from typing import Callable, Any, Union

from mercurial import extensions, commands
from mercurial.ui import ui as UI

from .cacheutils import HgCacheOperationError
from .cacheutils import initialize_cache
from .hgutils import hg_config
from .hgutils import hg_strip
from .hgutils import hg_have_out
from .hgutils import hg_config_set_default_remote
from .logger import log

# - it seems that while in `hg clone` `repo` is always a `bytes` source string,
# in `hg pull` it is some internal HG type that can change between hg/python versions
# - pylint used in prospector is too old and does not detect a typing hint
RepoType = Union[bytes, Any] # pylint: disable=unsubscriptable-object

OrigCommand = Callable[..., int]


def _clone_with_cache(orig: OrigCommand, ui: UI, repo: RepoType, *args: bytes, **opts) -> int:  # pragma: no cover
    if isinstance(repo, bytes):
        repo_s = repo.decode()
        target_dir = repo.split(b"/")[-1]
    else:
        ui.error("'repo' is {tp}, value={v}: do not know what to do with it".format(tp=type(repo), v=repo))
        return 1
    cache_dir = initialize_cache(ui, repo_s)
    log("cloning using cache at {cdir}".format(cdir=cache_dir), ui=ui)
    if args:
        target_dir = args[0]
    target_dir_s = target_dir.decode()
    args2 = (target_dir,) + args[1:]
    ret = orig(ui, cache_dir.encode(), *args2, **opts)
    hg_config_set_default_remote(target_dir_s, repo_s)
    return ret


def _pull_with_cache(orig: OrigCommand, ui: UI, repo: RepoType, *args: bytes, **opts) -> int:  # pragma: no cover
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
    args2 = (cache_dir.encode(),) + args[1:]
    return orig(ui, repo, *args2, **opts)


def uisetup(_):  # pragma: no cover
    extensions.wrapcommand(commands.table, b"clone", _clone_with_cache)
    extensions.wrapcommand(commands.table, b"pull", _pull_with_cache)
