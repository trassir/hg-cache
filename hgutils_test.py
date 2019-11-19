from hgcache.hgutils import hg_create_randomrepo
from hgcache.hgutils import hg_spoil_extra_changeset
from hgcache.hgutils import hg_spoil_missing_changeset
from hgcache.hgutils import hg_spoil_local_changes
from hgcache.hgutils import hg_config
from hgcache.hgutils import hg_config_set_default_remote
from hgcache.hgutils import hg_log
from hgcache.hgutils import hg_strip
from hgcache.hgutils import hg_diff
from hgcache.hgutils import hg_clone
from hgcache.hgutils import hg_pull
from hgcache.hgutils import hg_have_out
from hgcache.hgutils import hg_have_in


def test_hg_create_randomrepo(tmpdir):
    hg_create_randomrepo(str(tmpdir), 13)


def test_hg_spoil_extra_changeset(tmpdir):
    hg_create_randomrepo(str(tmpdir), 13)
    hg_spoil_extra_changeset(str(tmpdir))


def test_hg_spoil_missing_changeset(tmpdir):
    hg_create_randomrepo(str(tmpdir), 13)
    hg_spoil_missing_changeset(str(tmpdir))


def test_hg_spoil_local_changes(tmpdir):
    hg_create_randomrepo(str(tmpdir), 13)
    hg_spoil_local_changes(str(tmpdir))


def test_hg_config(prepare_repos):
    (local, cache, remote, foreign) = prepare_repos
    cfg = hg_config(remote)
    assert isinstance(cfg, dict)


def test_hg_config_set_default_remote(prepare_repos):
    (local, cache, remote, foreign) = prepare_repos
    hg_config_set_default_remote(remote, foreign)
    cfg = hg_config(remote)
    assert "paths.default" in cfg
    assert foreign == cfg["paths.default"]


def test_hg_log(prepare_repos):
    (local, cache, remote, foreign) = prepare_repos
    rc, out = hg_log(remote)
    assert rc == 0
    assert out != ""


def test_hg_strip(prepare_repos):
    (local, cache, remote, foreign) = prepare_repos
    hg_clone(local, remote)
    rc, out = hg_strip(remote, "1")
    assert rc == 0
    rc, out = hg_strip(local, "outgoing('%s')" % remote)
    assert rc == 0


def test_hg_diff(prepare_repos):
    (local, cache, remote, foreign) = prepare_repos
    rc, out = hg_diff(remote)
    assert rc == 0
    assert out == ""
    hg_spoil_local_changes(remote)
    rc, out = hg_diff(remote)
    assert rc == 0
    assert "localchange" in out


def test_hg_clone(prepare_repos):
    (local, cache, remote, foreign) = prepare_repos
    rc, out = hg_clone(local, remote)
    assert rc == 0


def test_hg_pull(prepare_repos):
    (local, cache, remote, foreign) = prepare_repos
    hg_clone(local, remote)
    hg_spoil_missing_changeset(local)
    rc, out = hg_pull(local, remote)
    assert rc == 0


def test_hg_have_out(prepare_repos):
    (local, cache, remote, foreign) = prepare_repos
    hg_clone(local, remote)
    rc, out = hg_have_out(local, remote)
    assert rc == 1
    hg_spoil_missing_changeset(remote)
    rc, out = hg_have_out(local, remote)
    assert rc == 0


def test_hg_have_in(prepare_repos):
    (local, cache, remote, foreign) = prepare_repos
    hg_clone(local, remote)
    rc, out = hg_have_in(local, remote)
    assert rc == 1
    hg_spoil_missing_changeset(local)
    rc, out = hg_have_in(local, remote)
    assert rc == 0
