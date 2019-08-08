# -*- coding: utf-8 -*-

# TODO: check - README should consist of nothing but words in
# templates and yaml. any other words and it's a sign the README/other
# docs have been manually edited.

import os
import sys
import time
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

import attr
from tqdm import tqdm
from face import Command, Flag, face_middleware
from boltons.fileutils import iter_find_files, atomic_save, mkdir_p

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

    util_cmd = Command(name='util', func=None)

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
    cmd.add(console)
    cmd.add(check)
    cmd.add(render)
    cmd.add(normalize)
    cmd.add(pull_repos)
    cmd.add(print_version, name='version')

    cmd.prepare()  # an optional check on all subcommands, not just the one being executed

    try:
        cmd.run(argv=argv)  # exit behavior is handled by mw_exit_handler
    except Exception:
        if os.getenv('APATITE_DEBUG'):
            import pdb;pdb.post_mortem()
        raise

    return


def console(plist, pdir):
    import pdb;pdb.set_trace()
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


@attr.s
class ProcessResult(object):
    returncode = attr.ib()
    stderr = attr.ib()
    stdout = attr.ib()
    start_time = attr.ib()
    end_time = attr.ib()

    @property
    def duration(self):
        return self.end_time - self.start_time


"""what's going to grab the pid for cancellation?

problems with concurrent futures:

* Why does the future need to know about the executor? Why can't we
create a future and submit that to the executor?

* It's seeming like I have to map arguments to futures and processes
to arguments, and then I can associate futures to processes?

"""

def _inner_future_call():
    # open a process
    # register a pid
    # communicate
    # register result? (or return result?)
    pass

FUTS = []
# atexit killall procs in non-done futs

def _future_call(executor, args, **kw):
    kw['stdout'] = subprocess.PIPE
    kw['stderr'] = subprocess.PIPE

    fut = executor.submit(subprocess.Popen, args, **kw)
    FUTS.append(fut)

    def _fut_done(fut):
        # note: new future execution is not started until done
        # callback is complete. basically, futures aren't really done
        # until their callbacks are, which is fine by me!
        if fut.cancelled():
            return
        started = time.time()
        proc = fut.result()
        stdout, stderr = proc.communicate()
        proc_res = ProcessResult(returncode=proc.returncode,
                                 stdout=stdout,
                                 stderr=stderr,
                                 start_time=started,
                                 end_time=time.time())
        fut.process_result = proc_res
        if proc_res.returncode == 0:
            executor.progress.update()
        else:
            print('%r exited with code %r, stderr:' % (proc.args, proc_res.returncode))
            print(proc_res.stderr)
        return

    fut.add_done_callback(_fut_done)

    return fut


def format_list(list_tmpl, *a, **kw):
    ret = []
    for text in list_tmpl:
        ret.append(text.format(*a, **kw))
    return ret


VCS_TMPLS = {'git': {'clone': ['{cmd}', 'clone', '{url}', '{target_dir}'],
                     'update': ['{cmd}', 'pull']},
             'hg': {'clone': ['{cmd}', 'clone', '{url}', '{target_dir}'],
                    'update': ['{cmd}', 'pull']},
             'bzr': {}}


def _pull_single_repo(executor, proj, repo_dir, rm_cached=False):
    # TODO: shouldn't this be the callable submitted to the executor?
    vcs, url = proj.clone_info
    target_dir = repo_dir + proj.name_slug + '/'
    cwd = repo_dir
    mode = 'clone'
    if os.path.exists(target_dir):
        if not rm_cached:
            mode = 'update'
            cwd = target_dir
        else:
            # sanity check we're in the right place
            if os.path.exists(target_dir + '../.apatite_repo_dir'):
                shutil.rmtree(target_dir)
            else:
                raise Exception('non-apatite path blocking apatite clone: %r' % target_dir)

    try:
        cmd_tmpl = VCS_TMPLS[vcs][mode]
    except KeyError:
        raise Exception('unsupported operation %r with vcs %r' % (mode, vcs))
    cmd = format_list(cmd_tmpl, cmd=vcs, url=url, target_dir=target_dir)
    # avoid asking for github username and password, since closing stdin doesn't work
    fut = _future_call(executor, cmd, cwd=cwd, env={'GIT_TERMINAL_PROMPT': '0'})
    return


def pull_repos(plist, work_dir=None):
    """
    clone or pull all projects. requires git, hg, and bzr to be installed for projects in APA
    """
    if work_dir is None:
        work_dir = os.path.expanduser('~/.apatite/')
        repo_dir = work_dir + 'repos/'
        mkdir_p(repo_dir)
        open(repo_dir + '/.apatite_repo_dir', 'w').close()
    try:
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.progress = tqdm(total=len(plist.project_list))
            for proj in plist.project_list:
                _pull_single_repo(executor, proj, repo_dir)
    except Exception:
        for fut in FUTS:
            if fut.done() and not fut.cancelled() and fut.result().returncode is None:
                fut.result().kill()
                # clean up incomplete paths
                if os.path.exists(fut.target_dir):
                    shutil.rmtree(fut.target_dir)
        raise

def show_missing_tags():
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
    file_path = file or 'projects.yaml'
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
