import ntpath

import pytest

from boltons import pathutils


@pytest.mark.parametrize('path,expected', [
    (r'C:\Users\Name', '~'), (r'c:\users\name', '~'),
    (r'c:\users\NAME\Project\file.txt', r'~\Project\file.txt'),
    (r'C:\Users\NameElsewhere\file.txt', r'C:\Users\NameElsewhere\file.txt'),
])
def test_shrinkuser_uses_windows_case_rules(monkeypatch, path, expected):
    for name in ('normpath', 'normcase', 'join'):
        monkeypatch.setattr(pathutils, name, getattr(ntpath, name), raising=False)
    monkeypatch.setattr(pathutils, 'expanduser', lambda _: r'C:\Users\Name')
    assert pathutils.shrinkuser(path) == expected
