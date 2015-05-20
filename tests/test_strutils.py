# -*- coding: utf-8 -*-

from boltons.strutils import asciify


def test_asciify():
    ref = u'Beyoncé'
    b = asciify(ref)
    assert len(b) == len(b)
    assert b[-1:].decode('ascii') == 'e'
