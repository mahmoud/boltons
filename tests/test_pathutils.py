"""Tests for boltons.pathutils.

The functions in ``pathutils`` ship with doctests covering their headline
examples, but the module had no dedicated unit-test file like the other
``*utils`` modules do. These tests focus on the parameter combinations and
edge cases the doctests do not exercise, following an Arrange/Act/Assert
layout.

All home-directory assertions are derived from ``expanduser('~')`` so the
suite is independent of the machine it runs on.
"""

from os.path import expanduser, normpath, join

from boltons.pathutils import augpath, shrinkuser, expandpath


# ---------------------------------------------------------------------------
# augpath
# ---------------------------------------------------------------------------

def test_augpath_no_arguments_returns_path_unchanged():
    # Arrange
    path = 'foo.bar'

    # Act
    result = augpath(path)

    # Assert
    assert result == 'foo.bar'


def test_augpath_replaces_directory():
    # Arrange: dpath replacement is documented but not doctested.
    path = 'foo.bar'

    # Act
    result = augpath(path, dpath='/tmp')

    # Assert
    assert result == join('/tmp', 'foo.bar')


def test_augpath_preserves_existing_directory():
    # Arrange: with no dpath given, the original directory must survive.
    path = join('a', 'b', 'foo.bar')

    # Act
    result = augpath(path, base='qux')

    # Assert
    assert result == join('a', 'b', 'qux.bar')


def test_augpath_combines_every_component():
    # Arrange: the kitchen-sink case, exercising all augmentations at once.
    path = 'foo.bar'

    # Act
    result = augpath(path, prefix='p_', base='bar', suffix='_s', ext='.baz')

    # Assert
    assert result == 'p_bar_s.baz'


def test_augpath_appends_extension_when_original_has_none():
    # Arrange
    path = 'foo'

    # Act
    result = augpath(path, ext='.txt')

    # Assert
    assert result == 'foo.txt'


def test_augpath_empty_ext_strips_extension():
    # Arrange: an explicit empty ext replaces (and so removes) the extension.
    path = 'foo.bar'

    # Act
    result = augpath(path, ext='')

    # Assert
    assert result == 'foo'


def test_augpath_multidot_true_suffix_keeps_compound_extension():
    # Arrange
    path = 'foo.tar.gz'

    # Act
    result = augpath(path, suffix='_new', multidot=True)

    # Assert
    assert result == 'foo_new.tar.gz'


def test_augpath_multidot_false_suffix_splits_on_last_dot():
    # Arrange
    path = 'foo.tar.gz'

    # Act
    result = augpath(path, suffix='_new', multidot=False)

    # Assert
    assert result == 'foo.tar_new.gz'


def test_augpath_multidot_true_ext_replaces_compound_extension():
    # Arrange: replacing the extension treats '.tar.gz' as a single extension.
    path = 'foo.tar.gz'

    # Act
    result = augpath(path, ext='.zip', multidot=True)

    # Assert
    assert result == 'foo.zip'


def test_augpath_multidot_false_ext_replaces_only_last_extension():
    # Arrange
    path = 'foo.tar.gz'

    # Act
    result = augpath(path, ext='.zip', multidot=False)

    # Assert
    assert result == 'foo.tar.zip'


# ---------------------------------------------------------------------------
# shrinkuser
# ---------------------------------------------------------------------------

def test_shrinkuser_replaces_exact_home_with_tilde():
    # Arrange
    home = expanduser('~')

    # Act
    result = shrinkuser(home)

    # Assert
    assert result == '~'


def test_shrinkuser_replaces_home_prefix_in_subpath():
    # Arrange
    home = expanduser('~')

    # Act
    result = shrinkuser(home + '/projects')

    # Assert
    assert result == join('~', 'projects')


def test_shrinkuser_does_not_shrink_when_no_separator_follows_home():
    # Arrange: a sibling directory whose name merely starts with the home
    # path should not be mistaken for the home directory itself.
    home = expanduser('~')
    sibling = home + 'extra'

    # Act
    result = shrinkuser(sibling)

    # Assert
    assert result == normpath(sibling)
    assert not result.startswith('~')


def test_shrinkuser_normalizes_redundant_separators():
    # Arrange: shrinkuser runs normpath, collapsing '//' and resolving '..'.
    home = expanduser('~')

    # Act
    result = shrinkuser(home + '/a//b/../c')

    # Assert
    assert result == join('~', 'a', 'c')


def test_shrinkuser_uses_custom_home_symbol_in_subpath():
    # Arrange
    home = expanduser('~')

    # Act
    result = shrinkuser(home + '/projects', home='$HOME')

    # Assert
    assert result == join('$HOME', 'projects')


def test_shrinkuser_uses_custom_home_symbol_for_exact_home():
    # Arrange: the custom symbol must also apply to the exact-home case.
    home = expanduser('~')

    # Act
    result = shrinkuser(home, home='$HOME')

    # Assert
    assert result == '$HOME'


def test_shrinkuser_leaves_non_home_path_unchanged():
    # Arrange
    path = '/etc/passwd'

    # Act
    result = shrinkuser(path)

    # Assert
    assert result == normpath('/etc/passwd')


# ---------------------------------------------------------------------------
# expandpath
# ---------------------------------------------------------------------------

def test_expandpath_expands_tilde_to_home():
    # Arrange
    path = '~'

    # Act
    result = expandpath(path)

    # Assert
    assert result == expanduser('~')


def test_expandpath_expands_environment_variable(monkeypatch):
    # Arrange
    monkeypatch.setenv('BOLTONS_TEST_VAR', 'eggs')

    # Act
    result = expandpath('$BOLTONS_TEST_VAR')

    # Assert
    assert result == 'eggs'


def test_expandpath_expands_tilde_and_variable_together(monkeypatch):
    # Arrange
    monkeypatch.setenv('BOLTONS_TEST_VAR', 'eggs')

    # Act
    result = expandpath('~/$BOLTONS_TEST_VAR')

    # Assert
    assert result == expanduser('~/eggs')


def test_expandpath_leaves_undefined_variable_untouched(monkeypatch):
    # Arrange: expandvars leaves unknown variables verbatim, like the shell.
    monkeypatch.delenv('BOLTONS_UNDEFINED_VAR', raising=False)

    # Act
    result = expandpath('$BOLTONS_UNDEFINED_VAR')

    # Assert
    assert result == '$BOLTONS_UNDEFINED_VAR'


def test_expandpath_leaves_plain_path_unchanged():
    # Arrange
    path = 'foo'

    # Act
    result = expandpath(path)

    # Assert
    assert result == 'foo'
