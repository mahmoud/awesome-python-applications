import glom
import json
import os
import urllib.request


API_KEY_ENV_VAR = 'GH_API_KEY'

required_cmds = {}
required_env_vars = {API_KEY_ENV_VAR: 'The GitHub API only allows 50 requests per hour for unauthenticated clients.'
                     '\nTo unlock 5000/hour, sent an env var with a token generated here: https://github.com/settings/tokens'
                     '\nIf this is your first time, it might help to follow the directions here:'
                     ' https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line.'
                     '\nNote that no special permissions are needed, so leave all/most of those checkboxes unchecked.'}


def collect(plist, project, repo_dir):

    host = project.repo_url.host
    if host != 'github.com':
        return {}
    GH_API_KEY = os.getenv(API_KEY_ENV_VAR)
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
