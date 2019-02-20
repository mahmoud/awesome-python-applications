# -*- coding: utf-8 -*-

# TODO: check - README should consist of nothing but words in
# templates and yaml. any other words and it's a sign the README/other
# docs have been manually edited.

import os
import sys

from face import Command, Flag, face_middleware
from boltons.fileutils import iter_find_files, atomic_save

from .dal import ProjectList
from .formatting import format_tag_toc, format_all_categories
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
    cmd.add(mw_ensure_project_listing)

    # add subcommands
    cmd.add(check)
    cmd.add(render)
    cmd.add(normalize)
    cmd.add(print_version, name='version')

    cmd.prepare()  # an optional check on all subcommands, not just the one being executed
    cmd.run(argv=argv)  # exit behavior is handled by mw_exit_handler

    return


def render(plist, pdir):
    topic_map = plist.get_projects_by_type('topic')
    topic_toc_text = format_tag_toc(topic_map)
    projects_by_topic = format_all_categories(topic_map)

    plat_map = plist.get_projects_by_type('platform')
    plat_toc_text = format_tag_toc(plat_map)
    projects_by_plat = format_all_categories(plat_map)

    context = {'TOPIC_TOC': topic_toc_text,
               'TOPIC_TEXT': projects_by_topic,
               'PLATFORM_TOC': plat_toc_text,
               'PLATFORM_TEXT': projects_by_plat,
               'TOTAL_COUNT': len(plist.project_list)}

    templates_path = pdir + '/templates/'
    if not os.path.isdir(templates_path):
        raise APACLIError('expected "templates" directory at %r' % templates_path)

    for filename in iter_find_files(templates_path, '*.tmpl.md'):
        tmpl_text = open(filename).read()
        target_filename = os.path.split(filename)[1].replace('.tmpl', '')
        output_text = tmpl_text.format(**context)
        with atomic_save(pdir + '/' + target_filename) as f:
            f.write(output_text.encode('utf8'))

    return


def check(plist):
    """
    [x] Check for the minimum set of keys.
    [x] Check all URLs valid format
    [x] Check no duplicate names (case normalized)
    [x] Check no duplicate repo_urls
    [x] Check no duplicate tags within the same project tag list
    [ ] Check all tags are in the tagsonomy

    All this stuff should probably be done before rendering
    anyways. Might need a check_urls subcommand though.

    """
    return 0


def show_no_cat(cat_name):
    """
    Show projects which are missing tags for a certain category.

    (this may be best covered by just rendering these into the docs.
    """


def normalize(plist, pfile):
    plist.normalize()
    new_yaml = plist.to_yaml()
    with atomic_save(pfile) as f:
        f.write(new_yaml.encode('utf8'))
    return


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

@face_middleware(provides=['plist', 'pdir', 'pfile'], optional=True)
def mw_ensure_project_listing(next_, file):
    file_path = file or 'protected.yaml'
    file_abs_path = os.path.abspath(file_path)

    if not os.path.exists(file_abs_path):
        raise APACLIError('Project listing not found: %s' % file_abs_path, 2)
    pdir = os.path.dirname(file_abs_path)
    plist = ProjectList.from_path(file_abs_path)
    return next_(plist=plist, pdir=pdir, pfile=file_abs_path)


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
