# -*- coding: utf-8 -*-

import os
import sys

from face import Command, Flag, face_middleware

from ._version import __version__

_ANSI_FORE_RED = '\x1b[31m'
_ANSI_FORE_GREEN = '\x1b[32m'
_ANSI_RESET_ALL = '\x1b[0m'

def _get_colorized_lines(lines):
    ret = []
    colors = {'-': _ANSI_FORE_RED, '+': _ANSI_FORE_GREEN}
    for line in lines:
        if line[0] in colors:
            line = colors[line[0]] + line + _ANSI_RESET_ALL
        ret.append(line)
    return ret


class APAError(Exception):
    pass

class APACLIError(APAError):
    "Raised when there's an error from user input or other CLI interaction"
    def __init__(self, msg=None, exit_code=1):
        self.msg = msg
        self.exit_code = exit_code
        if msg:
            super(APACLIError, self).__init__(msg)
        return


def main(argv=None):
    cmd = Command(name='apatite', func=None)  # func=None means output help

    # add flags
    cmd.add('--file', missing='projects.yaml',
            doc='path to the project listing YAML file')
    cmd.add('--confirm', parse_as=True,
            doc='show diff and prompt for confirmation before modifying the file')
    cmd.add('--non-interactive', parse_as=True,
            doc='disable falling back to interactive authentication, useful for automation')

    # add middlewares, outermost first ("first added, first called")
    cmd.add(mw_exit_handler)

    # add subcommands

    cmd.add(print_version, name='version')

    cmd.prepare()  # an optional check on all subcommands, not just the one being executed
    cmd.run(argv=argv)  # exit behavior is handled by mw_exit_handler

    return


def render():
    pass


def check():
    pass


def normalize():
    pass


def pull_repos():
    pass


def show_missing_tags():
    pass


def console():
    pass


"""
Read-only operations follow
"""

def print_version():
    'print the apatite version and exit'
    print('apatite version %s' % __version__)
    sys.exit(0)


"""
End subcommand handlers

Begin middlewares
"""

@face_middleware(provides=['plist'], optional=True)
def _ensure_project_listing(next_, file):
    file_path = file or 'protected.yaml'
    file_abs_path = os.path.abspath(file_path)

    if not os.path.exists(file_abs_path):
        raise APACLIError('Project listing not found: %s' % file_abs_path, 2)
    plist = ProjectList.from_path(file_abs_path)
    return next_(plist=plist)


@face_middleware
def mw_exit_handler(next_):
    status = 55  # should always be set to something else
    try:
        try:
            status = next_() or 0
        except APACLIError:
            raise
        except APAError as ppe:
            raise APACLIError(ppe.args[0])
    except KeyboardInterrupt:
        status = 130
        print('')
    except EOFError:
        status = 1
        print('')
    except APACLIError as ppce:
        if ppce.args:
            print('Error: ' + '; '.join([str(a) for a in ppce.args]))
        status = ppce.exit_code

    sys.exit(status)
    return
