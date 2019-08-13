# time tokei --output json > ~/tmp/tmp.json
# cat ~/tmp/tmp.json | python -m json.tool

import os
import json
import subprocess

SLOC_CMD = 'tokei'

required_cmds = {SLOC_CMD: 'install from https://github.com/XAMPPRocky/tokei/releases (put on path, chmod a+x)'}

_DEFAULT_IGNORED_LANGS = 'svg,ini,json,text'
IGNORED_LANGS = set([l.strip() for l in
                     os.getenv('APATITE_SLOC_IGNORE_LANGS', _DEFAULT_IGNORED_LANGS).split(',')])

_DEFAULT_IGNORED_FILES = 'translations,Language'  # freecad has a bunch of .ts files
IGNORED_FILES = set([l.strip() for l in
                     os.getenv('APATITE_SLOC_IGNORE_FILES', _DEFAULT_IGNORED_FILES).split(',')])

MERGE_HEADERS = not os.getenv('APATITE_NO_MERGE_HEADERS', '')

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


def _merge_headers(d, lang):
    lang_code = '%s_code' % lang
    header_key = '%sheader' % lang
    header_code_key = '%sheader_code' % lang
    if not d.get(header_key):
        return
    try:
        d[lang] += d[header_key]
        d[lang_code] += d[header_code_key]
    except KeyError:
        d[lang] = d[header_key]
        d[lang_code] = d[header_code_key]

    d.pop(header_key)
    d.pop(header_code_key)
    return


def collect(plist, project, repo_dir):
    cmd = [SLOC_CMD, '--output', 'json']
    for file_part in IGNORED_FILES:
        cmd.extend(['-e', file_part])
    proc_res = run_cap(cmd, cwd=repo_dir)

    data = json.loads(proc_res.stdout)
    data = data['inner']
    ret = {}
    for lang, stats in data.items():
        if not stats['lines'] or stats['inaccurate']:
            continue
        lang = lang.lower()
        if lang in IGNORED_LANGS:
            continue
        ret[lang] = stats['lines']
        ret[lang + '_code'] = stats['code']

    if MERGE_HEADERS:
        _merge_headers(ret, 'c')
        _merge_headers(ret, 'cpp')

    sorted_stats = sorted([(k, v) for k, v in ret.items() if k.endswith('_code')],
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
