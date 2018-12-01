# -*- encoding:utf-8 -*-
import os

import attr
from ruamel import yaml
from boltons.dictutils import OMD
from boltons.fileutils import iter_find_files, atomic_save

TOOLS_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_PATH = os.path.dirname(os.path.abspath(__file__)) + '/templates/'

house = u"\u2302"
BULLET = '*'
INDENT = ' ' * 4

@attr.s(frozen=True)
class TagEntry(object):
    tag = attr.ib()
    tag_type = attr.ib()
    title = attr.ib()
    desc = attr.ib(default='')
    subtags = attr.ib(default=(), repr=False)
    tag_path = attr.ib(default=(), repr=False)
    fq_tag = attr.ib(default=None)

    @property
    def is_fq(self):
        return self.tag == self.fq_tag


@attr.s(frozen=True)
class Project(object):
    name = attr.ib()
    desc = attr.ib(default='')
    tags = attr.ib(default=())
    urls = attr.ib(default=())

    @classmethod
    def from_dict(cls, d):
        kwargs = dict(d)
        cur_urls = ()
        for k in list(kwargs):
            if not k.endswith('_url'):
                continue
            cur_urls += ((k[:-4], kwargs.pop(k)),)
            kwargs['urls'] = cur_urls
        return cls(**kwargs)


def _unwrap_dict(d):
    if not len(d) == 1:
        raise ValueError('expected single-member dict')
    return list(d.items())[0]


class ProjectList(object):
    def __init__(self, project_list, tagsonomy):
        self.project_list = []
        self.tagsonomy = tagsonomy

        self.tag_registry = OMD()
        self.tag_alias_map = OMD()
        for tag in self.tagsonomy['topic']:
            self.register_tag('topic', tag)

        for project in project_list:
            self.project_list.append(Project.from_dict(project))

    @classmethod
    def from_path(cls, path):
        data = yaml.safe_load(open(path))
        return cls(data['projects'], data['tagsonomy'])

    def register_tag(self, tag_type, tag_entry, tag_path=()):
        if isinstance(tag_entry, str):
            tag, tag_entry = tag_entry, {}
        else:
            tag, tag_entry = _unwrap_dict(tag_entry)
            tag_entry = dict(tag_entry)
        tag_entry['tag'] = tag
        tag_entry['tag_type'] = tag_type

        if not tag_entry.get('title'):
            tag_entry["title"] = tag.replace('_', ' ').title()

        subtags = []
        for subtag_entry in tag_entry.pop('subtags', []):
            st = self.register_tag(tag_type, subtag_entry,
                                   tag_path=(tag,) if not tag_path else tag_path + (tag,))
            subtags.append(st)
        tag_entry['subtags'] = tuple(subtags)
        tag_entry['fq_tag'] = '.'.join(tag_path + (tag,))
        if not tag_path:
            ret = TagEntry(**tag_entry)
        else:
            ret = TagEntry(tag_path=tag_path, **tag_entry)

        self.tag_registry[tag] = ret
        return ret

    def get_projects_by_type(self, type_name):
        ret = OMD()
        for tag, tag_entry in self.tag_registry.items():
            if tag_entry.tag_type != type_name:
                continue
            ret[tag_entry] = []
            for project in self.project_list:
                if tag in project.tags:
                    ret[tag_entry].append(project)
        return ret

    def get_tags_by_type(self, type_name):
        return [te for te in self.tag_registry.values() if te.tag_type == type_name]


# sort of document the expected ones, even when they match the
# .title() pattern
_URL_LABEL_MAP = {'wp': 'Wikipedia',
                  'home': 'Home',
                  'repo': 'Repo',
                  'docs': 'Docs'}


def _format_url_name(name):
    return _URL_LABEL_MAP.get(name, name.title())



def format_category(project_map, tag_entry):
    lines = []
    append = lines.append

    def _format_tag(project_map, tag_entry, level=2):
        append('%s <a id="tag-%s" href="#%s">%s</a>' %
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
            links = ', '.join(['[%s](%s)' % (_format_url_name(name), url) for name, url in sorted(project.urls)])

            line = tmpl.format(bullet=BULLET, name=project.name, links=links, desc=project.desc)
            if len(project.tags) > 1:
                line += ' `(%s)`' % ', '.join(sorted([t for t in project.tags if t != tag_entry.tag]))
            lines.append(line)

        append('')
        return '\n'.join(lines)

    return _format_tag(project_map, tag_entry)


def format_tag_toc(tag_registry):
    lines = []

    def _format_tag_toc(tag_entries, path=()):
        for te in tag_entries:
            if te.tag_path != path:
                continue
            link_text = '<a href="#tag-%s">%s</a>' % (te.fq_tag or te.tag, te.title)
            lines.append((INDENT * len(te.tag_path)) + BULLET + ' ' + link_text)
            if te.subtags:
                _format_tag_toc(te.subtags, path=path + (te.tag,))
                link_text = '<a href="#tag-%s-other">Other %s projects</a>' % (te.fq_tag or te.tag, te.title)
                lines.append((INDENT * (len(te.tag_path) + 1)) + BULLET + ' ' + link_text)
        return

    _format_tag_toc(tag_registry)

    return '\n'.join(lines)


def format_all_categories(project_map):
    parts = []
    for tag_entry in project_map:
        if tag_entry.tag_path:
            continue
        if not project_map[tag_entry]:
            continue  # TODO: some message, inviting additions
        text = format_category(project_map, tag_entry)
        parts.append(text)

    return '\n'.join(parts)


def main():
    plist = ProjectList.from_path('projects.yaml')
    readme = open(TEMPLATES_PATH + '/README.tmpl.md').read()

    topic_map = plist.get_projects_by_type('topic')
    topic_toc_text = format_tag_toc(plist.get_tags_by_type('topic'))
    projects_by_topic = format_all_categories(topic_map)

    context = {'TOPIC_TOC': topic_toc_text,
               'TOPIC_TEXT': projects_by_topic,}

    # readme = readme.replace('[TOP]', topic_toc_text)
    # readme = readme.replace('[PROJECTS_BY_TOPIC]', projects_by_topic)

    for filename in iter_find_files(TEMPLATES_PATH, '*.tmpl.md'):
        tmpl_text = open(filename).read()
        target_filename = os.path.split(filename)[1].replace('.tmpl', '')
        output_text = tmpl_text.format(**context)
        with atomic_save(target_filename) as f:
            f.write(output_text.encode('utf8'))

    return


if __name__ == '__main__':
    main()
