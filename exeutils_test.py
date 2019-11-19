from exeutils import SubcommandException


def test_SubcommandException():
    e = SubcommandException(
        1337, "subdir", ["foo.exe", "--bar", "--baz"], "output text")
    assert ("%s" % e) != ""
