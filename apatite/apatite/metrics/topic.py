

def collect(plist, project, repo_dir):
    topics = _get_topics(plist, project)
    return {'primary': topics[0],
            'secondary': topics[1]}

def _get_topics(plist, project):
    tags = [t for t in project._tags if t in plist.tag_registry]  # TODO: why is _tags underscored again?

    topic_tags = [t for t in tags if plist.tag_registry[t].tag_type == 'topic']

    if not topic_tags:
        print(project.name)
        return None, None
    elif len(topic_tags) == 1:
        return topic_tags[0], None
    return topic_tags[0], topic_tags[1]
