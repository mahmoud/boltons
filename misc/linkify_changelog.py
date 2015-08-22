
import re
import sys

BASE_RTD_URL = 'http://boltons.readthedocs.org/en/latest/'
BASE_ISSUES_URL = 'https://github.com/mahmoud/boltons/issues/'

_issues_re = re.compile('#(\d+)')
_member_re = re.compile('((\w+utils)\.[a-zA-Z0-9_.]+)')


def sub_member_match(match):
    full_name = match.group(1)
    mod_name = match.group(2)
    url = BASE_RTD_URL + mod_name + '.html#boltons.' + full_name
    ret = '[%s](%s)' % (full_name, url)
    # print ret
    return ret


def sub_issue_match(match):
    link_text = match.group(0)
    issue_num = match.group(1)
    link_target = BASE_ISSUES_URL + issue_num
    ret = '[%s](%s)' % (link_text, link_target)
    # print ret
    return ret


def main():
    try:
        cl_filename = sys.argv[1]
    except IndexError:
        cl_filename = 'CHANGELOG.md'
    cl_text = open(cl_filename).read().decode('utf-8')
    ret = _member_re.sub(sub_member_match, cl_text)
    ret = _issues_re.sub(sub_issue_match, ret)
    print ret


if __name__ == '__main__':
    main()
