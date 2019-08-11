
import re
import subprocess
from collections import Counter

from boltons.timeutils import isoparse

required_cmds = []

def collect(project, repo_dir):
    """
    TODO:

    first_commit_date   "git rev-list --max-parents=0 HEAD"
    last_commit_date
    committer_count   "git shortlog --summary --numbered --email"   # might need to be deduped by name
    commit_count
    committer_dist    // fixed buckets, proportionalized to commit_count (# of committers that did 90% of commits, 80%, 70%, etc.)
    """
    vcs_name = project.clone_info[0]
    ret = {'vcs_name': vcs_name}
    if vcs_name == 'git':
        ret.update(get_git_info(repo_dir))
    return ret



def run_cap(args, **kw):
    kw['stdout'] = subprocess.PIPE
    kw['stderr'] = subprocess.PIPE
    kw.setdefault('encoding', 'utf8')
    # slightly worried about ignoring utf8 decode errors on git
    # output, bc the git docs say they recode to utf8 (this came up bc
    # unicode characters in committer names)
    # https://git-scm.com/docs/git-show/1.8.2.2
    kw.setdefault('errors', 'replace')

    return subprocess.run(args, **kw)


def _get_commit_dt(repo_dir, commit_hash, **kw):
    kw.setdefault('env', {})['TZ'] = 'UTC'
    kw['cwd'] = repo_dir
    proc_res = run_cap(['git', 'show', '-s', '--format=%cd', '--date=format-local:%Y-%m-%dT%H:%M:%S', commit_hash], **kw)
    date_text = proc_res.stdout.strip()
    return isoparse(date_text)


_git_committer_re = re.compile(r'^\s+(?P<commit_count>\d+)\s+(?P<name>.*)\s<(?P<email>[^>]*)>$', re.MULTILINE | re.UNICODE)

def get_git_info(repo_dir):
    ret = {}

    proc_res = run_cap(['git', 'rev-list', '--max-parents=0', 'HEAD'], cwd=repo_dir)
    first_commit_hashes = proc_res.stdout.strip().split()

    first_commit_dt = sorted([_get_commit_dt(repo_dir, fch) for fch in first_commit_hashes])[0]

    proc_res = run_cap(['git', 'rev-parse', 'HEAD'], cwd=repo_dir)
    latest_commit_hash = proc_res.stdout.strip()

    latest_commit_dt = _get_commit_dt(repo_dir, latest_commit_hash)

    ret['first_commit'] = first_commit_dt.isoformat()
    ret['latest_commit'] = latest_commit_dt.isoformat()

    proc_res = run_cap(['git', 'shortlog', '--summary', '--numbered', '--email'], cwd=repo_dir)

    _commits_by_name = Counter()
    _commits_by_email = Counter()
    for match in _git_committer_re.finditer(proc_res.stdout):
        gdict = match.groupdict()
        gdict['commit_count'] = int(gdict['commit_count'])
        _commits_by_name[gdict['name']] += gdict['commit_count']
        _commits_by_email[gdict['email']] += gdict['commit_count']


    ret['commit_count'] = commit_count = sum(_commits_by_name.values())
    ret['committer_count'] = len(_commits_by_name)
    ret['committer_email_count'] = len(_commits_by_email)

    threshes = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]
    commit_thresh_map = {thresh: (commit_count * thresh) for thresh in threshes}

    sorted_committers = sorted(_commits_by_name.items(), reverse=True, key=lambda x: x[1])
    def _get_proportion_count(thresh_commit_count):
        _cur_commit_count = 0
        _cur_committer_count = 0
        for committer, committer_commit_count in sorted_committers:
            if _cur_commit_count > thresh_commit_count:
                break
            _cur_commit_count += committer_commit_count
            _cur_committer_count += 1
        return _cur_committer_count

    # how many developers's commits together comprise XX% of the commits?
    committer_dist_map = {thresh: _get_proportion_count(thresh_commit_count)
                          for thresh, thresh_commit_count in commit_thresh_map.items()}
    ret['committer_dist'] = committer_dist_map
    ret['top_5'] = [round(c / commit_count, 4) for _, c in sorted_committers][:5]
    ret['minor_committer_counts'] = {x: len([c for _, c in sorted_committers if c <= x])
                                     for x in range(1, 6)}

    '''
    # DEBUG
    print(first_commit_dt.isoformat(), latest_commit_dt.isoformat(), latest_commit_dt - first_commit_dt)
    from pprint import pprint
    pprint(committer_dist_map)
    pprint(ret['top_5'])
    pprint(ret)
    raise SystemExit  # quits after the first
    '''
    return ret
