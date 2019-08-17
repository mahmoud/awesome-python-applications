
import itertools
import os
import re

from boltons.dictutils import OMD
from boltons.iterutils import first
# from boltons.fileutils import iter_find_files  # vendored to include dirs

from apatite.utils import run_cap

RG_CMD = 'rg'
VERSION_CMD = 'vermin'

required_cmds = {RG_CMD: 'install from https://github.com/BurntSushi/ripgrep/releases (put on path, chmod a+x)',
                 VERSION_CMD: 'install version 0.6.0 of vermin from: https://pypi.org/project/vermin/#description'}

# probably going to have to manually code this up in here, and then
# modify the tagsonomy posthoc once things start looking coherent

def _join_patt_any_order(patt1, patt2):
    return '({0}.*{1})|({1}.*{0})'.format(patt1, patt2)


IMPORT_MAP = {'server': {'server_framework': ['django',
                                              'flask',
                                              'zope',
                                              'web2py',
                                              'pylons',
                                              'pyramid',
                                              'bottle'],},
              'desktop': {'gui_framework': ['qt',
                                            'gtk',
                                            'wx',
                                            'kivy',
                                            'pygame']},
              None: {'concurrency': ['gevent',
                                     'twisted',
                                     'tornado',
                                     'concurrent\\.futures',
                                     'asyncio',
                                     ]}}  # i also checked for trio, but got a false positive in freecad


FREEZERS = ['pyinstaller', 'cx_Freeze', 'py2exe', 'py2app', 'pynsist']
CONTAINER_FILES = ['snapcraft.yaml', 'appimage', 'flatpak', 'Dockerfile']


def collect(plist, project, repo_dir):
    ret = {}
    ret['type'] = arch_type = _get_arch_type(plist, project)
    # proc_res = run_cap([RG_CMD])
    # raise SystemExit()

    if arch_type == 'unknown':
        print(arch_type, project.name)

    ret['dep'] = dep_map = {}
    if arch_type not in IMPORT_MAP:
        return ret

    _all_arches = IMPORT_MAP[None].items()
    for col, dep_names in itertools.chain(IMPORT_MAP[arch_type].items(), _all_arches):
        dep_res_map = {}
        for dep_name in dep_names:
            search_output = search_files(_join_patt_any_order('import', dep_name), '*.py', repo_dir)
            dep_res_map[dep_name] = search_output.splitlines()
        top_dep, top_dep_res = sorted(dep_res_map.items(), key=lambda x: len(x[1]))[-1]
        if top_dep_res:
            dep_map[col] = top_dep

    ret['pkg'] = _get_pkg_info(plist, project, repo_dir)

    ret['compat'] = _get_py_version(plist, project, repo_dir)
    '''
    # See comment at bottom of file
    if ret['type'] == 'server' and ret['pkg'].get('freezer'):
        print('server with freezer', project.name, ret['pkg']['freezer'])
    if ret['type'] == 'desktop' and ret['pkg'].get('container'):
        print('desktop with container', project.name, ret['pkg']['container'])
    '''
    return ret


def search_files(patt, file_patt, repo_dir):
    cmd = [RG_CMD]
    if file_patt:
        cmd.extend(['-g', file_patt])
    cmd.append(patt)
    proc_res = run_cap(cmd, cwd=repo_dir)
    return proc_res.stdout


# copied in from boltons to add include_dirs
import re
import fnmatch
basestring = (str, bytes)
def iter_find_files(directory, patterns, ignored=None, include_dirs=False):
    """Returns a generator that yields file paths under a *directory*,
    matching *patterns* using `glob`_ syntax (e.g., ``*.txt``). Also
    supports *ignored* patterns.

    Args:
        directory (str): Path that serves as the root of the
            search. Yielded paths will include this as a prefix.
        patterns (str or list): A single pattern or list of
            glob-formatted patterns to find under *directory*.
        ignored (str or list): A single pattern or list of
            glob-formatted patterns to ignore.

    For example, finding Python files in the current directory:

    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> os.path.basename(filenames[-1])
    'urlutils.py'

    Or, Python files while ignoring emacs lockfiles:

    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    .. _glob: https://en.wikipedia.org/wiki/Glob_%28programming%29

    """
    if isinstance(patterns, basestring):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, basestring):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    for root, dirs, files in os.walk(directory):
        if include_dirs:
            for basename in dirs:
                if pats_re.match(basename):
                    if ignored and ign_re.match(basename):
                        continue
                    filename = os.path.join(root, basename)
                    yield filename

        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return



def _get_arch_type(plist, project):
    '''type: desktop, server, mobile, browser
    install_targets: windows, mac, linux, android, ...
    web frameworks: django, flask, other  (tornado, zope, etc.)
    gui_frameworks: gtk, qt, qt4, qt5, qt45, tk, wx, pygame, kivy, beeware, other
    cli_frameworks: argparse, optparse, click, etc.
    container: docker, flatpak, snap, appimage

    Is docker a target? Is docker linux?

    desktop with install target linux is different than server, where
    linux is all but assumed. docker implies server.

    basic definitions:
    * desktop = mostly single-user/local software.
    * server = mostly multi-user software
    * mobile/browser = a little less unclear

    TODO: what to do about deluge, which is single-user, but also has
    a multi-user-accessible server mode? or jupyter which is
    single-user but has a server architecture? probably have to tie-break based on

    '''

    tags = [t for t in project._tags if t in plist.tag_registry]  # TODO: why is _tags underscored again?

    if 'server' in tags:
        return 'server'
    desktop_tags = [t for t in tags if 'desktop' in plist.tag_registry[t].tag_path]
    if desktop_tags:
        return 'desktop'
    mobile_tags = [t for t in tags if 'mobile' in plist.tag_registry[t].tag_path]
    if mobile_tags:
        return 'mobile'
    return 'unknown'


def _get_pkg_info(plist, project, repo_dir):
    # snap: search for snapcraft.yaml
    # appimage: find -iname "appimage" -type d
    # flatpak: find -iname "flatpak" -type d  # maybe exclude test dirs, e.g., what ansible has
    # docker: find -name "Dockerfile"
    ret = {}
    container_stacks = OMD()
    for path in iter_find_files(repo_dir, CONTAINER_FILES, include_dirs=True):
        container_stacks.add(os.path.splitext(os.path.basename(path))[0].lower(), path)
    #if container_stacks:
    #    print(container_stacks.todict())
    has_docker = bool(container_stacks.pop('dockerfile', None))
    container_stack = first(container_stacks.keys(), None) or ('docker' if has_docker else '')
    ret['container'] = container_stack

    # TODO: split into mac/windows/linux? for linux I'll need to look
    # at deb/rpm, and I'm not sure the best strategy there. rpm maybe
    # .spec files? might have to check inside as other tools
    # (pyinstaller) uses .spec, too.

    # freezers -> pyInstaller, cx_Freeze, py2exe, py2app, pynsist
    # (bbFreeze phased out, osnap/constructor not yet adopted, harder
    # to search for). conda and omnibus also not adopted.

    freezer_res_map = OMD()
    for freezer_name in FREEZERS:
        search_output = search_files(freezer_name, '*', repo_dir)
        if search_output:
            freezer_res_map.add(freezer_name, len(search_output.splitlines()))
    if freezer_res_map:
        top, top_res = sorted(freezer_res_map.items(), key=lambda x: x[1])[-1]
        ret['freezer'] = top

    return ret


def _get_py_version(plist, project, repo_dir):

    # -v flag required because it improves the correctness of detection
    # manual tests on the calibre package showed better results with -v
    cmd = [VERSION_CMD, '-v', repo_dir]
    proc_res = run_cap(cmd, cwd=repo_dir)
    # hardcoded strings to search output lines for
    MIN_VERSION_PATTERN = '^Minimum required versions:'
    INCOMP_VERSION_PATTERN = '^Incompatible versions:'

    lines = proc_res.stdout.splitlines()
    min_version_line = None
    incomp_version_line = None
    # with -v flag a lot of output is generated, the lines containing
    # version information will probably be at the bottom
    for line in lines[-5:]:
        if re.match(MIN_VERSION_PATTERN, line):
            min_version_line = line
        if re.match(INCOMP_VERSION_PATTERN, line):
            incomp_version_line = line

    # None indicates not compatible with that major version of python
    py_2_version = None
    py_3_version = None
    if min_version_line is not None:
        supp_versions = min_version_line[26:].split()
        for version in supp_versions:
            if version[0] == '2':
                py_2_version = version.strip(',')
            elif version[0] == '3':
                py_3_version = version.strip(',')

    return {'min_py2': py_2_version, 'min_py3': py_3_version}


''' Some interesting results that illustrate how server/desktop
packaging aren't really that disjoint. Some of the docker ones are
desktop applications for developers, or use docker for development
setup, but others are legit:

desktop with container ArchiveBox docker
server with freezer Deluge py2app
server with freezer SABnzbd pyinstaller
desktop with container ZeroNet docker
desktop with container cartoonify / Draw This. docker
desktop with container FreeCAD docker
desktop with container Meshroom docker
desktop with container OCRopus docker
server with freezer Octoprint py2exe
desktop with container Ranger docker
desktop with container PyMedusa docker
desktop with container Bitmessage docker
desktop with container Hangups snapcraft
desktop with container Mailpile docker
server with freezer MoinMoin py2exe
desktop with container TahoeLAFS docker
desktop with container InVesalius docker
desktop with container Manim docker
desktop with container Sage Math docker
desktop with container Mercurial docker
server with freezer Review Board py2exe
desktop with container Ansible docker
desktop with container pgcli docker
server with freezer StackStorm py2exe
desktop with container MITMproxy docker
server with freezer Pupy py2exe
server with freezer Spiderfoot py2exe
desktop with container Universal Radio Hacker (URH) docker
desktop with container Komodo Edit docker
desktop with container pipenv docker
desktop with container yum docker
server with freezer buildbot py2exe
desktop with container Meson docker
desktop with container Pants docker
desktop with container asciinema docker
desktop with container Home Assistant docker
'''
