# -*- coding: utf-8 -*-

import sys

from boltons.iterutils import join

def test_join():
    joined = [(0, 0, None),
             (1, 1, None),
             (2, 2, None),
             (3, 3, None),
             (4, None, None),
             (5, None, 5),
             (6, None, 6),
             (7, None, 7),
             (8, None, 8),
             (9, None, 9),
             (None, None, 10),
             (None, None, 11),
             (None, None, 12),
             (None, None, 13),
             (None, None, 14)]
    
    assert list(join([range(10),range(4),range(5,15)])) == joined

       
