
from apatite.utils import run_cap

RG_CMD = 'rg'

required_cmds = {RG_CMD: 'install from https://github.com/BurntSushi/ripgrep/releases (put on path, chmod a+x)'}

# probably going to have to manually code this up in here, and then
# modify the tagsonomy posthoc once things start looking coherent

def _join_patt_any_order(patt1, patt2):
    return '({0}.*{1})|({1}.*{0})'.format(patt1, patt2)


INTERESTING_IMPORTS = ['django',
                       'flask',
                       'twisted',
                       'tornado']


def collect(plist, project, repo_dir):
    ret = {}
    ret['type'] = arch_type = _get_arch_type(plist, project)
    # proc_res = run_cap([RG_CMD])
    # raise SystemExit()

    if arch_type == 'unknown':
        print(arch_type, project.name)

    dep_map = {}
    for dep_name in INTERESTING_IMPORTS:
        dep_map[dep_name] = search_reqs(_join_patt_any_order('import', dep_name), '*.py', repo_dir)[:20]

    ret['dep'] = dep_map

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
