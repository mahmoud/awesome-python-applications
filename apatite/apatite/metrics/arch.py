
import itertools

from apatite.utils import run_cap

RG_CMD = 'rg'

required_cmds = {RG_CMD: 'install from https://github.com/BurntSushi/ripgrep/releases (put on path, chmod a+x)'}

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
            search_output = search_reqs(_join_patt_any_order('import', dep_name), '*.py', repo_dir)
            dep_res_map[dep_name] = search_output.splitlines()
        top_dep, top_dep_res = sorted(dep_res_map.items(), key=lambda x: len(x[1]))[-1]
        if top_dep_res:
            dep_map[col] = top_dep

    return ret


def search_reqs(patt, file_patt, repo_dir):
    cmd = ['rg']
    if file_patt:
        cmd.extend(['-g', file_patt])
    cmd.append(patt)
    proc_res = run_cap(cmd, cwd=repo_dir)
    return proc_res.stdout


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
