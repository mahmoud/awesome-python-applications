
from boltons.iterutils import soft_sorted

# house = u"\u2302"
BULLET = '1.'
INDENT = ' ' * 4

# sort of document the expected ones, even when they match the
# .title() pattern
_URL_LABEL_MAP = {'wp': 'WP',
                  'home': 'Home',
                  'repo': 'Repo',
                  'docs': 'Docs',
                  'pypi': 'PyPI'}

_URL_ORDER = ['repo', 'home', 'wp', 'docs']


def _format_url_name(name):
    return _URL_LABEL_MAP.get(name, name.title())


def format_category(project_map, tag_entry):
    lines = []
    append = lines.append

    def _format_tag(project_map, tag_entry, level=2):
        append('%s <a id="tag-%s" href="#tag-%s">%s</a>' %
               ('#' * level, tag_entry.fq_tag or tag_entry.tag, tag_entry.fq_tag or tag_entry.tag, tag_entry.title))
        append('')
        if tag_entry.desc:
            append(tag_entry.desc)
            append('')
        if tag_entry.subtags:
            append('')
            for subtag_entry in tag_entry.subtags:
                _format_tag(project_map, subtag_entry, level=level + 1)
            append('%s <a id="tag-%s-other" href="#tag-%s-other">Other %s projects</a>' %
                   ('#' * (level + 1), tag_entry.tag, tag_entry.tag, tag_entry.title))

        for project in project_map[tag_entry]:
            tmpl = '  {bullet} **{name}** - ({links}) {desc}'
            urls = [u for u in project.urls if u[0] != 'clone']  # clone_urls aren't for display
            links = ', '.join(['[%s](%s)' % (_format_url_name(name), url) for name, url
                               in soft_sorted(urls, key=lambda x: x[0], first=_URL_ORDER[:-1], last=_URL_ORDER[-1:])])

            line = tmpl.format(bullet=BULLET, name=project.name, links=links, desc=project.desc)
            if len(project._tags) > 1:
                other_tags = [t for t in project._tags if t != tag_entry.tag]
                line += ' `(%s)`' % ', '.join(other_tags)
            lines.append(line)

        append('')
        return '\n'.join(lines)

    return _format_tag(project_map, tag_entry)


def format_tag_toc(project_map):
    lines = []

    def _format_tag_toc(tag_entries, path=()):
        for te in tag_entries:
            if te.tag_path != path:
                continue
            entry_count = len(project_map[te])
            if te.subtags:
                entry_count = len(project_map[te]) + len(set.union(*[set(project_map[st]) for st in te.subtags]))
            link_text = '<a href="#tag-%s">%s</a> *(%s)*' % (te.fq_tag or te.tag, te.title, entry_count)
            lines.append((INDENT * len(te.tag_path)) + BULLET + ' ' + link_text)
            if te.subtags:
                _format_tag_toc(te.subtags, path=path + (te.tag,))
                if len(project_map[te]):
                    link_text = ('<a href="#tag-%s-other">Other %s projects</a> *(%s)*'
                                 % (te.fq_tag or te.tag, te.title, len(project_map[te])))
                    lines.append((INDENT * (len(te.tag_path) + 1)) + BULLET + ' ' + link_text)
        return

    _format_tag_toc(project_map.keys())

    return '\n'.join(lines)


def format_all_categories(project_map):
    parts = []
    for tag_entry in project_map:
        if tag_entry.tag_path:
            continue
        if not project_map[tag_entry] and not tag_entry.subtags:
            continue  # TODO: some message, inviting additions
        text = format_category(project_map, tag_entry)
        parts.append(text)

    return '\n'.join(parts)
