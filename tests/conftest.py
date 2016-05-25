import sys
import re


_VERSION_MARKER = re.compile('_py(?P<version>\d)')


def pytest_ignore_collect(path, config):
    """
    Ignore tests that end with _pyX, where X does not equal this
    interpreter's major version.
    """
    filename = path.basename
    modulename = filename.split('.', 1)[0]
    match = _VERSION_MARKER.search(modulename)
    return match and not int(match.group('version')) == sys.version_info[0]
