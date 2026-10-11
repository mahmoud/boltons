from os.path import expanduser, join, normpath

from boltons.pathutils import augpath, shrinkuser, expandpath


def test_augpath():
    assert augpath('foo.bar') == 'foo.bar'
    assert augpath('foo.bar', dpath='/tmp') == join('/tmp', 'foo.bar')
    assert augpath(join('a', 'b', 'foo.bar'), base='qux') == join('a', 'b', 'qux.bar')
    assert augpath('foo.bar', prefix='p_', base='bar', suffix='_s', ext='.baz') == 'p_bar_s.baz'
    assert augpath('foo', ext='.txt') == 'foo.txt'
    assert augpath('foo.bar', ext='') == 'foo'


def test_augpath_multidot():
    assert augpath('foo.tar.gz', suffix='_new', multidot=True) == 'foo_new.tar.gz'
    assert augpath('foo.tar.gz', suffix='_new', multidot=False) == 'foo.tar_new.gz'
    assert augpath('foo.tar.gz', ext='.zip', multidot=True) == 'foo.zip'
    assert augpath('foo.tar.gz', ext='.zip', multidot=False) == 'foo.tar.zip'


def test_shrinkuser():
    home = expanduser('~')
    assert shrinkuser(home) == '~'
    assert shrinkuser(home + '/projects') == join('~', 'projects')
    # a sibling path that merely starts with the home string is not shrunk
    assert shrinkuser(home + 'extra') == normpath(home + 'extra')
    assert shrinkuser(home + '/a//b/../c') == join('~', 'a', 'c')
    assert shrinkuser(home + '/projects', home='$HOME') == join('$HOME', 'projects')
    assert shrinkuser(home, home='$HOME') == '$HOME'
    assert shrinkuser('/etc/passwd') == normpath('/etc/passwd')


def test_expandpath(monkeypatch):
    assert expandpath('~') == expanduser('~')
    monkeypatch.setenv('BOLTONS_TEST_VAR', 'eggs')
    assert expandpath('$BOLTONS_TEST_VAR') == 'eggs'
    assert expandpath('~/$BOLTONS_TEST_VAR') == expanduser('~/eggs')
    monkeypatch.delenv('BOLTONS_UNDEFINED_VAR', raising=False)
    assert expandpath('$BOLTONS_UNDEFINED_VAR') == '$BOLTONS_UNDEFINED_VAR'
    assert expandpath('foo') == 'foo'
