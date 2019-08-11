# time tokei --output json > ~/tmp/tmp.json
# cat ~/tmp/tmp.json | python -m json.tool

import os
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


def _dir_file_count(path):
    dir_count, file_count = 0, 0
    for root, dirs, files in os.walk(path):
        dir_count += len([d for d in dirs if not d.startswith('.')])
        file_count += len(files)
    return dir_count, file_count


def collect(project, repo_dir):
    proc_res = run_cap([SLOC_CMD, '--output', 'json'], cwd=repo_dir)

    data = json.loads(proc_res.stdout)
    data = data['inner']
    ret = {}
    for lang, stats in data.items():
        ret[lang.lower()] = stats['lines']
        ret[lang.lower() + '_code'] = stats['code']

    sorted_stats = sorted([(k, v['code']) for k, v in data.items()],
                          reverse=True, key=lambda x: x[1])
    ret.update({'TOTAL_%s' % key: sum([s[key] for s in data.values()])
                for key in ['blanks', 'code', 'comments', 'lines']})

    ratio_map = {}
    for lang, count in sorted_stats[:5]:
        ratio = round(count / ret['TOTAL_code'], 2)
        if ratio < 0.1:
            break
        ratio_map[lang.lower()] = ratio
    ratio_map['OTHER'] = round(1.0 - sum(ratio_map.values()), 2) if sorted_stats else 1.0

    ret['RATIO'] = ratio_map
    ret['TOTAL_dirs'], ret['TOTAL_files'] = _dir_file_count(repo_dir)

    return ret
