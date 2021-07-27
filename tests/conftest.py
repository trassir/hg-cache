import pytest

from hg_cache.hgutils import hg_create_randomrepo


@pytest.fixture(scope='function')
def prepare_repos(tmpdir_factory):
    # local is the directory where actual working directory is supposed to be after `hg clone`
    local = ("%s" % tmpdir_factory.mktemp("local")).replace("\\", "/")
    # cache is the directory used to speed up `hg clone`
    cache = ("%s" % tmpdir_factory.mktemp("cache")).replace("\\", "/")
    # remote is the repo from which we `hg clone`
    remote = ("%s" % tmpdir_factory.mktemp("remote")).replace("\\", "/")

    hg_create_randomrepo(remote, 3)
    return (local, cache, remote)

@pytest.fixture(scope='function')
def foreign_repo(tmpdir_factory):
    # remote is another repo unrelevant to the current repository
    foreign = ("%s" % tmpdir_factory.mktemp("foreign")).replace("\\", "/")

    hg_create_randomrepo(foreign, 3)
    return foreign
