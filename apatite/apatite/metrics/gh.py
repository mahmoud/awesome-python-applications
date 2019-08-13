import glom
import json
import os
import urllib.request


DETECT_CMD = 'curl'
DETECT_ENV = 'GH_API_KEY'

required_cmds = {DETECT_CMD: 'install via your package manager'}
required_env_vars = [DETECT_ENV]


def collect(project, repo_dir):

    host = project.repo_url.host
    if host != 'github.com':
        return {}
    GH_API_KEY = os.getenv(DETECT_ENV)
    api_url = 'https://api.github.com/repos/%s/%s' % (project.author,
                                                      project.repo_name)
    request = urllib.request.Request(api_url)
    request.add_header('Authorization', 'token %s' % GH_API_KEY)
    response = urllib.request.urlopen(request)
    api_json = json.loads(response.read())
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
