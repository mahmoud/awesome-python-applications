import datetime
import glom
import json
import os
import subprocess

from apatite.cli import ProcessResult

DETECT_CMD = 'curl'
DETECT_ENV = 'GH_API_KEY'

required_cmds = {DETECT_CMD: 'install via your package manager'}
required_env_vars = [DETECT_ENV]


def collect(project, repo_dir):

    host = project.repo_url.host
    if host != 'github.com':
        return {}
    started = datetime.datetime.utcnow()
    GH_API_KEY = os.getenv(DETECT_ENV)
    api_url = 'https://api.github.com/repos/%s/%s' % (project.author, project.repo_name)
    proc = subprocess.Popen([DETECT_CMD, '-L', '-H', 'Authorization: token %s' % GH_API_KEY, api_url],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    proc_res = ProcessResult(returncode=proc.returncode,
                             stdout=stdout.decode('utf8'),
                             stderr=stderr,
                             start_time=started,
                             end_time=datetime.datetime.utcnow())
    api_json = json.loads(proc_res.stdout)
    glom_spec = {
        'size': 'size',
        'stars': 'stargazers_count',
        'watchers': 'subscribers_count',
        'forks': 'forks',
        'open_issues': 'open_issues',
        'license': glom.Coalesce('license.name', default=None),
        'has_wiki': 'has_wiki',
    }
    return glom.glom(api_json, glom_spec)
