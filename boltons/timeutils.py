# -*- coding: utf-8 -*-

import datetime


def relative_datetime(d, other=None):
    # TODO: add decimal rounding factor (default 0)
    if other is None:
        other = datetime.datetime.utcnow()
    diff = other - d
    s, days = diff.seconds, diff.days
    if days > 7 or days < 0:
        return d.strftime('%d %b %y')
    elif days == 1:
        return '1 day ago'
    elif days > 1:
        return '{0} days ago'.format(diff.days)
    elif s < 5:
        return 'just now'
    elif s < 60:
        return '{0} seconds ago'.format(s)
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{0} minutes ago'.format(s / 60)
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{0} hours ago'.format(s / 3600)
