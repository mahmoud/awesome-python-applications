# time tokei --output json > ~/tmp/tmp.json
# cat ~/tmp/tmp.json | python -m json.tool

import json
import subprocess

SLOC_CMD = 'tokei'

required_cmds = {SLOC_CMD: 'install from https://github.com/XAMPPRocky/tokei/releases (put on path, chmod a+x)'}

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


def collect(project, repo_dir):
    proc_res = run_cap([SLOC_CMD, '--output', 'json'], cwd=repo_dir)

    data = json.loads(proc_res.stdout)
    data = data['inner']
    ret = {}
    for lang, stats in data.items():
        stats.pop('stats')  # per-file stats not necessary
        if stats.get('inaccurate'):
            continue
        stats.pop('inaccurate')
        ret[lang.lower()] = stats
    ret['total'] = {key: sum([s[key] for s in ret.values()])
                    for key in ['blanks', 'code', 'comments', 'lines']}
    return ret
