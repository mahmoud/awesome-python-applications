# -*- coding: utf-8 -*-

# TODO: check - README should consist of nothing but words in
# templates and yaml. any other words and it's a sign the README/other
# docs have been manually edited.

import os
import imp
import sys
import json
import time
import shutil
import datetime
import subprocess
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed

import attr
from tqdm import tqdm
from face import Command, Flag, face_middleware, ListParam
from boltons.fileutils import iter_find_files, atomic_save, mkdir_p, iter_find_files
from boltons.timeutils import isoparse, parse_timedelta
from boltons.jsonutils import JSONLIterator
from boltons.setutils import IndexedSet
from boltons.iterutils import remap

from .dal import ProjectList
from .formatting import format_tag_toc, format_all_categories
from ._version import __version__

_ANSI_FORE_RED = '\x1b[31m'
_ANSI_FORE_GREEN = '\x1b[32m'
_ANSI_RESET_ALL = '\x1b[0m'

CUR_PATH = os.path.dirname(os.path.abspath(__file__))
METRICS_PATH = os.path.join(CUR_PATH, 'metrics')


def print_err(*a, **kw):
    kw['file'] = sys.stderr
    return print(*a, **kw)


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


def _date_param(text):
    text = text.strip()
    if text.startswith('-'):
        td = parse_timedelta(text)
        dt = datetime.datetime.utcnow() + td  # adding a negative
        return dt
    dt = isoparse(text)
    return dt


def main(argv=None):
    """\
    automation and analytics for curated lists of awesome software.

    Normal analysis workflow:

      * apatite pull-repos  (can take 3-4 hours, 25GB on the full APA, use --targets to limit)
      * apatite collect-metrics
      * apatite collate  # TODO
      * apatite analyze  # TODO
    """
    cmd = Command(name='apatite', func=None, doc=main.__doc__)  # func=None means output help

    # add flags
    cmd.add('--file', missing='projects.yaml',
            doc='path to the project listing YAML file')
    cmd.add('--confirm', parse_as=True,
            doc='show diff and prompt for confirmation before modifying the file')
    cmd.add('--non-interactive', parse_as=True,
            doc='disable falling back to interactive authentication, useful for automation')
    cmd.add('--targets', parse_as=ListParam(str), missing=[], doc='specific target projects')
    cmd.add('--metrics', parse_as=ListParam(str), missing=[], doc='specific metrics to collect')
    cmd.add('--dry-run', parse_as=True, doc='do not save results')
    two_weeks_ago = _date_param('-2w')
    cmd.add('--earliest', parse_as=_date_param, missing=two_weeks_ago,
            doc=('minimum datetime value to accept (isodate or negative timedelta).'
                 ' defaults to two weeks ago (-2w)'))

    # add middlewares, outermost first ("first added, first called")
    cmd.add(mw_exit_handler)
    cmd.add(mw_ensure_project_listing)
    cmd.add(mw_ensure_work_dir)

    # add subcommands
    cmd.add(render)
    cmd.add(normalize)
    cmd.add(pull_repos)
    cmd.add(collect_metrics)
    cmd.add(collate_metrics)
    cmd.add(show_recent_metrics)
    cmd.add(console)
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
    "use pdb to explore plist and pdir"
    import pdb;pdb.set_trace()
    return


def render(plist, pdir):
    "generate the list markdown from the yaml listing"
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
    """normalize project and tag order, checking for duplicates
    and format divergences, overwrites the yaml listing"""
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

def format_list(list_tmpl, *a, **kw):
    ret = []
    for text in list_tmpl:
        ret.append(text.format(*a, **kw))
    return ret


VCS_TMPLS = {'git': {'clone': ['{cmd}', 'clone', '{url}', '{target_dir}'],
                     'update': ['{cmd}', 'pull']},  # update is run from within target_dir
             'hg': {'clone': ['{cmd}', 'clone', '{url}', '{target_dir}'],
                    'update': ['{cmd}', 'pull']},
             'bzr': {'clone': ['{cmd}', 'branch', '{url}'],
                     'update': ['{cmd}', 'pull']}}
CUR_PROCS = []


def _pull_single_repo(proj, repo_dir, rm_cached=False):
    # TODO: turn rm_cached into a flag
    # TODO: shouldn't this be the callable submitted to the executor?
    vcs, url = proj.clone_info
    if url is None:
        print_err('project "%s" has unsupported vcs type for repo url: %r' % (proj.name, proj.repo_url))
        return  # TODO
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

    cur_dt = datetime.datetime.utcnow()
    started = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env={'GIT_TERMINAL_PROMPT': '0'})
    proc.project_name = proj.name_slug
    proc.target_dir = target_dir
    CUR_PROCS.append(proc)
    stdout, stderr = proc.communicate()
    CUR_PROCS.remove(proc)
    proc_res = ProcessResult(returncode=proc.returncode,
                             stdout=stdout.decode('utf8'),
                             stderr=stderr,
                             start_time=started,
                             end_time=datetime.datetime.utcnow()) # Bug? duratiion, start_time - end_time TypeError
    if proc_res.returncode != 0:
        print_err('%r exited with code %r, stderr:' % (proc.args, proc_res.returncode))
        print_err(proc_res.stderr)
    else:
        with atomic_save(target_dir + '/.apatite_last_pulled') as f:
            f.write(cur_dt.isoformat().partition('.')[0].encode('utf8'))

    return proc_res


def pull_repos(plist, targets, repo_dir, verbose=False):
    """
    clone or pull all projects. requires git, hg, and bzr to be installed for projects in APA
    """
    successes = []
    try:
        project_list = plist.project_list
        if targets:
            project_list = [proj for proj in project_list if (proj.name in targets or proj.name_slug in targets)]
        with ThreadPoolExecutor(max_workers=5) as executor, tqdm(total=len(project_list)) as progress:
            futs = []

            for proj in project_list:
                fut = executor.submit(_pull_single_repo, proj, repo_dir)
                fut.project = proj
                futs.append(fut)

            for fut in as_completed(futs):
                progress.update()
                progress.set_description(desc='(%s)' % ', '.join([fut.project.name_slug for fut in futs if fut.running()]))
                exc = fut.exception()
                if exc is not None:
                    print_err('%s got exception %r' % (fut.project.name_slug, exc))
                    continue
                proc_res = fut.result()
                if not proc_res:
                    continue  # TODO
                if proc_res.returncode == 0:
                    successes.append(fut.project)
                if verbose:
                    print(proc_res.stdout)
    finally:
        for proc in CUR_PROCS:
            if proc.returncode:
                continue
            proc.kill()
            # clean up incomplete paths
            if os.path.exists(proc.target_dir):
                shutil.rmtree(proc.target_dir)
    print()
    if successes:
        print('successfully pulled %s project(s): %s' % (len(successes), ', '.join([p.name_slug for p in successes])))
    else:
        print('failed to pull any projects')
    return


class ProjectProcessor(object):
    # TODO
    def __init__(self, func, args):
        self.futs = []
        self.func = func
        self.args = args

    @property
    def results(self):
        return [f.result() for f in self.futs]

    def process(self):
        # TODO: basically the generic parts of pull_repos
        pass


def _get_project_repo_info_map(project_list, repo_dir):
    ret = OrderedDict()

    for project in project_list:
        target_repo_dir = os.path.join(repo_dir, project.name_slug)
        if not os.path.isdir(target_repo_dir):
            print_err('project %s repo directory not found at: %r' % (project.name, target_repo_dir))
            continue
        pull_date_path = target_repo_dir + '/.apatite_last_pulled'
        with open(pull_date_path, 'r') as f:
            last_pulled_bytes = f.read()
            try:
                last_pulled = isoparse(last_pulled_bytes)
            except (TypeError, ValueError):
                print_err('project %s had unreadable pull date at: %r' % (project.name, pull_date_path))
                continue
        ret[project] = (target_repo_dir, last_pulled)

    return ret


def _get_all_metric_mods():
    ret = []
    for metric_path in iter_find_files(METRICS_PATH, '*.py', ignored='__init__.py'):
        mod_name = os.path.splitext(os.path.split(metric_path)[-1])[0]
        metric_mod = imp.load_source(mod_name, metric_path)
        if not callable(getattr(metric_mod, 'collect', None)):
            print_err('skipping non-metric module at %r' % metric_path)
            continue
        required_cmds = getattr(metric_mod, 'required_cmds', {})
        missing_cmds = []
        if required_cmds:
            for cmd, instr_text in required_cmds.items():
                cmd_path = shutil.which(cmd)
                if cmd_path is None:
                    print_err('missing command "%s", required by metric "%s". Installation instructions:\n\n%s\n'
                              % (cmd, metric_mod.__name__, instr_text))
                    missing_cmds.append(cmd)
        if missing_cmds:
            print_err('omitting metric "%s" due to missing commands: %s (see installation instructions above)'
                      % (metric_mod.__name__, ', '.join(missing_cmds)))
        else:
            ret.append(metric_mod)
    return ret


def collect_metrics(plist, repo_dir, metrics_dir, targets=None, metrics=None, dry_run=False):
    "use local clones of repositories (from pull-repos) to gather data about projects"
    project_list = plist.project_list
    if targets:
        project_list = [proj for proj in project_list if (proj.name in targets or proj.name_slug in targets)]

    metric_mods = all_metric_mods = _get_all_metric_mods()
    if metrics:
        metric_mods = [m for m in metric_mods if m.__name__ in metrics]

    if not metric_mods:
        print_err('failed to collect data. no known metrics selected (available: %s)' % ', '.join([m.__name__ for m in all_metric_mods]))
        return

    project_repo_map = _get_project_repo_info_map(project_list, repo_dir)

    if not project_repo_map:
        print_err('failed to collect data on any projects')
        return

    res_fn_tmpl = 'apatite-metrics__{run_dt}__{newest_dt}__{oldest_dt}.jsonl'

    newest_dt = max([last_pulled for _, last_pulled in project_repo_map.values()])
    oldest_dt = min([last_pulled for _, last_pulled in project_repo_map.values()])

    res_fn = res_fn_tmpl.format(run_dt=datetime.datetime.utcnow().isoformat(),
                                # TODO: upgrade req to 3.6 and make isofromat('minutes'),
                                newest_dt=newest_dt.isoformat().rsplit(':', 1)[0],
                                oldest_dt=oldest_dt.isoformat().rsplit(':', 1)[0])

    print('collecting data for metrics: %s' % ', '.join([m.__name__ for m in metric_mods]))
    for metric_mod in metric_mods:
        with tqdm(total=len(project_repo_map), unit='run') as cur_metric_progress:
            for project, (target_repo_dir, last_pulled) in project_repo_map.items():
                cur_metric_progress.set_description(f'{metric_mod.__name__}: {project.name_slug}'.ljust(20))
                start_time = time.time()
                try:
                    res = metric_mod.collect(project, target_repo_dir)
                except KeyboardInterrupt:
                    return
                except Exception as e:
                    print_err('%s metric failed on project %s with exception %r. (run with APATITE_DEBUG=1 to debug.)'
                              % (metric_mod.__name__, project.name_slug, e))
                    if os.getenv('APATITE_DEBUG'):
                        import pdb;pdb.post_mortem()
                    continue
                entry = {'project': project.name_slug,
                         'metric_name': metric_mod.__name__,
                         'result': res,
                         'pull_date': last_pulled.isoformat(),
                         '~ms': round((time.time() - start_time) * 1000, 2)}

                res_json = json.dumps(entry, sort_keys=True)
                if not dry_run:
                    with open(os.path.join(metrics_dir, res_fn), 'a') as f:
                        f.write(res_json + '\n')
                cur_metric_progress.update()
    return


def show_recent_metrics(metrics_dir):
    "shows the most recent metrics collection"
    metrics_files = sorted(iter_find_files(metrics_dir, '*.jsonl'), reverse=True)
    if not metrics_files:
        print_err('no recent metrics found at %s' % metrics_dir)
        return
    metrics_file = metrics_files[0]
    print('#  ' + os.path.basename(metrics_file) + '\n')
    for line in open(metrics_file):
        try:
            print(line, end='')
        except IOError:
            break
    return


def collate_metrics(plist, earliest, metrics_dir, metrics=None, output_path=None, output_format=None):
    metric_mods = all_metric_mods = _get_all_metric_mods()
    if metrics:
        metric_mods = [m for m in metric_mods if m.__name__ in metrics]
    if not metric_mods:
        print_err('failed to collect data. no known metrics selected (available: %s)' % ', '.join([m.__name__ for m in all_metric_mods]))
        return

    metrics_map = {(m.__name__, p.name_slug): None for m in all_metric_mods for p in plist.project_list}
    print(len(metrics_map))

    metrics_files = iter_find_files(metrics_dir, '*.jsonl')
    earliest_text = earliest.isoformat()
    files_to_search = []
    for metric_file in metrics_files:
        metric_base_fn = os.path.basename(os.path.splitext(metric_file)[0])
        _, run_dt_text, newest_dt_text, oldest_dt_text = metric_base_fn.split('__')
        if newest_dt_text < earliest_text:
            print('skipping', metric_file)
            continue
        files_to_search.append(metric_file)

        with open(metric_file) as f:
            # TODO: possible optimization when searching for a
            # specific project/metric. search for the project name
            # slug and metric name in the part of the line before the
            # result begins (the jsonl keys are carefully chosen to
            # sort nicely)
            for line_data in JSONLIterator(f):
                metric_name, proj_slug = line_data['metric_name'], line_data['project']
                try:
                    cur_data = metrics_map[metric_name, proj_slug]
                except KeyError:
                    # not a tracked project/metric
                    continue
                if cur_data is None or cur_data['pull_date'] < line_data['pull_date']:
                    metrics_map[metric_name, proj_slug] = line_data

    possible_paths = IndexedSet()
    for (metric_name, proj_slug), data in metrics_map.items():
        if data is None:
            continue
        def _visit(path, key, value):
            if not isinstance(value, (list, dict)):
                possible_paths.add((metric_name,) + path + (key,))
            return True
        remap(data['result'], visit=_visit)

    # TODO: deal with missing metrics
    # TODO: output csv or something

    from pprint import pprint
    pprint(sorted(possible_paths))
    print(len(possible_paths))


class MetricsCollector(object):
    # maybe someday
    def __init__(self, project_list):
        self.project_processor = ProjectProcessor(self._collect_one, project_list)


def show_missing_tags():
    pass

# TODO: eventually going to need a command to migrate names in result files

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


@face_middleware(provides=['work_dir', 'repo_dir', 'metrics_dir'], optional=True)
def mw_ensure_work_dir(next_):
    work_dir = os.path.expanduser('~/.apatite/')
    repo_dir = work_dir + 'repos/'
    mkdir_p(repo_dir)
    open(repo_dir + '/.apatite_repo_dir', 'w').close()
    metrics_dir = work_dir + 'metrics/'
    mkdir_p(metrics_dir)
    return next_(work_dir=work_dir, repo_dir=repo_dir, metrics_dir=metrics_dir)


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
