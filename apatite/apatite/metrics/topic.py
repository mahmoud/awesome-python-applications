

def collect(plist, project, repo_dir):
    topics = _get_topics(plist, project)
    return {'primary': topics[0],
            'primary_fq': topics[1],
            'secondary': topics[2],
            'secondary_fq': topics[3]}

def _get_topics(plist, project):
    tags = [t for t in project._tags if t in plist.tag_registry]  # TODO: why is _tags underscored again?

    topic_tags = [t for t in tags if plist.tag_registry[t].tag_type == 'topic']

    primary = None
    secondary = None
    if not topic_tags:
        print(project.name)
    elif len(topic_tags) >= 1:
        primary = topic_tags[0]
    if len(topic_tags) >= 2:
        secondary = topic_tags[1]

    return (primary, plist.tag_registry[primary].fq_tag if primary else None,
            secondary, plist.tag_registry[secondary].fq_tag if secondary else None)
