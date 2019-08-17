
import subprocess

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
