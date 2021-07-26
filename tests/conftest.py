#!/usr/bin/env python2

import pytest
from hgutils import hg_create_randomrepo


@pytest.fixture(scope='function')
def prepare_repos(tmpdir_factory):
    local = ("%s" % tmpdir_factory.mktemp("local")).replace("\\", "/")
    cache = ("%s" % tmpdir_factory.mktemp("cache")).replace("\\", "/")
    remote = ("%s" % tmpdir_factory.mktemp("remote")).replace("\\", "/")
    foreign = ("%s" % tmpdir_factory.mktemp("foreign")).replace("\\", "/")
    hg_create_randomrepo(remote, 3)
    hg_create_randomrepo(foreign, 5)
    return (local, cache, remote, foreign)
