# -*- coding: utf-8 -*-

from boltons import strutils


def test_asciify():
    ref = u'Beyoncé'
    b = strutils.asciify(ref)
    assert len(b) == len(b)
    assert b[-1:].decode('ascii') == 'e'


def test_indent():
    to_indent = '\nabc\ndef\n\nxyz\n'
    ref = '\n  abc\n  def\n\n  xyz\n'
    assert strutils.indent(to_indent, '  ') == ref
