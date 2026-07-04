import os
from os.path import expanduser, join, normpath

from boltons.pathutils import augpath, expandpath, shrinkuser


def test_augpath_no_op():
    assert augpath('foo.bar') == 'foo.bar'


def test_augpath_replace_extension():
    assert augpath('foo.bar', ext='.BAZ') == 'foo.BAZ'


def test_augpath_suffix_and_prefix():
    assert augpath('foo.bar', suffix='_') == 'foo_.bar'
    assert augpath('foo.bar', prefix='_') == '_foo.bar'


def test_augpath_replace_base():
    assert augpath('foo.bar', base='baz') == 'baz.bar'


def test_augpath_combined():
    result = augpath('foo.bar', suffix='_suff', prefix='pref_', ext='.baz', base='bar')
    assert result == 'pref_bar_suff.baz'


def test_augpath_multidot():
    # With multidot the extension begins at the first dot.
    assert augpath('foo.tar.gz', ext='.zip', multidot=True) == 'foo.zip'
    assert augpath('foo.tar.gz', suffix='_new', multidot=True) == 'foo_new.tar.gz'
    # Without multidot only the final dot delimits the extension.
    assert augpath('foo.tar.gz', ext='.zip', multidot=False) == 'foo.tar.zip'


def test_augpath_replace_directory():
    path = join('a', 'b', 'foo.bar')
    assert augpath(path, dpath=join('x', 'y')) == join('x', 'y', 'foo.bar')


def test_shrinkuser_replaces_home_with_tilde():
    home = expanduser('~')
    assert home != '~'
    assert shrinkuser(home) == '~'


def test_shrinkuser_keeps_subpath():
    home = expanduser('~')
    assert shrinkuser(join(home, 'code')) == join('~', 'code')


def test_shrinkuser_custom_symbol():
    home = expanduser('~')
    assert shrinkuser(home, '$HOME') == '$HOME'
    assert shrinkuser(join(home, '1'), '$HOME') == join('$HOME', '1')


def test_shrinkuser_leaves_non_home_paths():
    # Sharing a prefix with home without a separator boundary is not a match.
    home = expanduser('~')
    assert shrinkuser(home + 'X') == normpath(home + 'X')


def test_expandpath_expands_env_and_user():
    os.environ['BOLTONS_TEST_SPAM'] = 'eggs'
    assert expandpath('$BOLTONS_TEST_SPAM') == 'eggs'
    assert expandpath('~') == expanduser('~')


def test_expandpath_leaves_plain_paths():
    assert expandpath('foo') == 'foo'
