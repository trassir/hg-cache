from hgutils import hg_create_randomrepo
from hgutils import hg_spoil_extra_changeset
from hgutils import hg_spoil_missing_changeset
from hgutils import hg_spoil_local_changes
from hgutils import hg_config
from hgutils import hg_config_set_default_remote
from hgutils import hg_log
from hgutils import hg_strip
from hgutils import hg_diff
from hgutils import hg_clone
from hgutils import hg_pull
from hgutils import hg_have_out
from hgutils import hg_have_in


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
    (_, _, remote, _) = prepare_repos
    cfg = hg_config(remote)
    assert isinstance(cfg, dict)


def test_hg_config_set_default_remote(prepare_repos):
    (_, _, remote, foreign) = prepare_repos
    hg_config_set_default_remote(remote, foreign)
    cfg = hg_config(remote)
    assert "paths.default" in cfg
    assert foreign == cfg["paths.default"]


def test_hg_log(prepare_repos):
    (_, _, remote, _) = prepare_repos
    rc, out = hg_log(remote)
    assert rc == 0
    assert out != ""


def test_hg_strip(prepare_repos):
    (local, _, remote, _) = prepare_repos
    hg_clone(local, remote)
    rc, _ = hg_strip(remote, "1")
    assert rc == 0
    rc, _ = hg_strip(local, "outgoing('%s')" % remote)
    assert rc == 0


def test_hg_diff(prepare_repos):
    (_, _, remote, _) = prepare_repos
    rc, out = hg_diff(remote)
    assert rc == 0
    assert out == ""
    hg_spoil_local_changes(remote)
    rc, out = hg_diff(remote)
    assert rc == 0
    assert "localchange" in out


def test_hg_clone(prepare_repos):
    (local, _, remote, _) = prepare_repos
    rc, _ = hg_clone(local, remote)
    assert rc == 0


def test_hg_pull(prepare_repos):
    (local, _, remote, _) = prepare_repos
    hg_clone(local, remote)
    hg_spoil_missing_changeset(local)
    rc, _ = hg_pull(local, remote)
    assert rc == 0


def test_hg_have_out(prepare_repos):
    (local, _, remote, _) = prepare_repos
    hg_clone(local, remote)
    rc, _ = hg_have_out(local, remote)
    assert rc == 1
    hg_spoil_missing_changeset(remote)
    rc, _ = hg_have_out(local, remote)
    assert rc == 0


def test_hg_have_in(prepare_repos):
    (local, _, remote, _) = prepare_repos
    hg_clone(local, remote)
    rc, _ = hg_have_in(local, remote)
    assert rc == 1
    hg_spoil_missing_changeset(local)
    rc, _ = hg_have_in(local, remote)
    assert rc == 0
