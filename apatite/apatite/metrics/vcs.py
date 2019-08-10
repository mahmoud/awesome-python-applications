
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
    if vcs_name != 'git':
        return ret
