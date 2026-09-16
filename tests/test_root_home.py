import os

from boltons.pathutils import shrinkuser


def test_shrinkuser_when_home_is_filesystem_root(monkeypatch):
    root = os.path.abspath(os.sep)
    monkeypatch.setattr('boltons.pathutils.expanduser', lambda path: root)
    assert shrinkuser(root) == '~'
    assert shrinkuser(os.path.join(root, 'project', 'file')) == os.path.join('~', 'project', 'file')
    assert shrinkuser(os.path.join(root, 'file'), '$HOME') == os.path.join('$HOME', 'file')
