#!/usr/bin/env python2

import os
import pytest
from cacheutils import cache_with_subdir
from hgutils import hg_create_randomrepo


@pytest.fixture(scope='function')
def prepare_repos(tmpdir_factory):
    local = ("%s" % tmpdir_factory.mktemp("local")).replace("\\", "/")
    cache_root = ("%s" % tmpdir_factory.mktemp("cache")).replace("\\", "/")
    remote = ("%s" % tmpdir_factory.mktemp("remote")).replace("\\", "/")
    cache_specific = cache_with_subdir(cache_root, remote)
    os.makedirs(cache_specific)
    foreign = ("%s" % tmpdir_factory.mktemp("foreign")).replace("\\", "/")
    hg_create_randomrepo(remote, 3)
    hg_create_randomrepo(foreign, 5)
    return (local, cache_root, cache_specific, remote, foreign)
