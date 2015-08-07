import os
import subprocess
from datetime import datetime


def get_commit_id():
    suffix = ''
    commit = 'unversioned'
    if os.path.exists('.git'):
        desc = subprocess.check_output('git describe --dirty --always --long --abbrev=40'.split()).strip()
        desc = desc.split('-')
        if desc[-1].strip() == 'dirty':
            suffix = '_uncommitted-changes'
            desc.pop()
        commit = desc[-1].strip('g')
    elif os.path.exists('.hg'):
        desc = subprocess.check_output('hg id --id --debug'.split()).strip()
        if desc[-1] == '+':
            suffix = '_uncommitted-changes'
        commit = desc.strip('+')
    return '%s_%s%s' % (commit, get_current_time(), suffix)


def get_current_time():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def first_or_false(obj):
    if obj:
        value, = obj
    else:
        value = False

    return value

