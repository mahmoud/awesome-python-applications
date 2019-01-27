# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import io
import os
import copy

import attr
from ruamel.yaml import YAML, round_trip_load
from ruamel.yaml.comments import CommentedMap
from boltons.dictutils import OMD
from boltons.fileutils import iter_find_files, atomic_save

TOOLS_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_PATH = os.path.dirname(os.path.abspath(__file__)) + '/templates/'

# house = u"\u2302"
BULLET = '1.'
INDENT = ' ' * 4


def to_yaml(obj):
    sio = io.StringIO()
    yaml = YAML()
    yaml.width = 2000
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.dump(obj, sio)
    return sio.getvalue()



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
    _orig_data = attr.ib(default=None, repr=False, cmp=False)

    @classmethod
    def from_dict(cls, d):
        kwargs = dict(d)
        kwargs['tags'] = tuple(kwargs.get('tags', ()))
        cur_urls = ()
        for k in list(kwargs):
            if not k.endswith('_url'):
                continue
            cur_urls += ((k[:-4], kwargs.pop(k)),)
            kwargs['urls'] = cur_urls
        kwargs['orig_data'] = d
        return cls(**kwargs)

    def to_dict(self):
        # deepcopy necessary to maintain comments
        ret = copy.deepcopy(self._orig_data) if self._orig_data else CommentedMap()
        # print(to_yaml(ret), end='')
        ret['name'] = self.name
        ret['desc'] = self.desc
        ret['tags'] = self.tags
        for url_type, url in self.urls:
            ret[url_type + '_url'] = url
        return ret


def _unwrap_dict(d):
    if not len(d) == 1:
        raise ValueError('expected single-member dict')
    return list(d.items())[0]


class ProjectList(object):
    def __init__(self, project_list, tagsonomy):
        self.project_list = []
        self.tagsonomy = tagsonomy

        self.tag_registry = OMD()

        for tag_group in ('topic', 'platform'):  # TODO: framework, license
            for tag in self.tagsonomy[tag_group]:
                self.register_tag(tag_group, tag)

        for project in project_list:
            new_tags = soft_sorted(project.get('tags', []), first=self.tag_registry.keys())
            project['tags'] = new_tags
            self.project_list.append(Project.from_dict(project))

    @classmethod
    def from_path(cls, path):
        data = round_trip_load(open(path, encoding='utf-8'))
        return cls(data['projects'], data['tagsonomy'])

    def to_dict(self):
        ret = CommentedMap()
        ret['tagsonomy'] = self.tagsonomy
        plist = []
        seen_topics = set()
        for p in self.project_list:
            cur_pdict = p.to_dict()
            plist.append(cur_pdict)

            # now, determine whether to emit a comment
            topic_tags = [t for t in p.tags
                          if t in self.tag_registry
                          and self.tag_registry[t].tag_type == 'topic']
            if not topic_tags:
                continue
            first_topic = topic_tags[0]
            if first_topic in seen_topics:
                continue
            seen_topics.add(first_topic)
            cur_pdict.yaml_set_start_comment('\n' + first_topic.title() + '\n\n')

        ret['project_list'] = plist
        return ret

    def to_yaml(self):
        return to_yaml(self.to_dict())

    def normalize(self):
        # sort project list by first topic tag and name (lexi).
        tag_list = list(self.tag_registry.keys())
        def plist_sort_key(project):
            topic_tags = [t for t in project.tags
                          if t in self.tag_registry
                          and self.tag_registry[t].tag_type == 'topic']
            first_topic = topic_tags[0] if topic_tags else 'misc'  # TODO: might change to uncategorized in future
            first_topic_idx = tag_list.index(first_topic)
            return (first_topic_idx, project.name.lower())

        project_list = []
        for project in sorted(self.project_list, key=plist_sort_key):
            if not project.desc[-1:] in ').':
                project = attr.evolve(project, desc=project.desc + '.')
            project_list.append(project)

        self.project_list = project_list
        return

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
            ret[tag_entry].sort(key=lambda x: x.name.lower())
        return ret


# sort of document the expected ones, even when they match the
# .title() pattern
_URL_LABEL_MAP = {'wp': 'WP',
                  'home': 'Home',
                  'repo': 'Repo',
                  'docs': 'Docs',
                  'pypi': 'PyPI'}

_URL_ORDER = ['repo', 'home', 'wp', 'docs']


def soft_sorted(iterable, first=None, last=None, key=None, reverse=False):
    """For when you care about the order of some elements, but not about
    others.

    Use this to float to the top and/or sink to the bottom a specific
    ordering, while sorting the rest of the elements according to
    normal :func:`sorted` rules.

    >>> soft_sorted(['two', 'b', 'one', 'a'], first=['one', 'two'])
    ['one', 'two', 'a', 'b']
    >>> soft_sorted(range(7), first=[6, 15], last=[2, 4], reverse=True)
    [6, 5, 3, 1, 0, 2, 4]

    Args:
       iterable (list): A list or other iterable to sort.
       first (list): A sequence to enforce for elements which should
          appear at the beginning of the returned list.
       last (list): A sequence to enforce for elements which should
          appear at the end of the returned list.
       key (callable): Callable used to generate a comparable key for
          each item to be sorted, same as the key in
          :func:`sorted`. Note that entries in *first* and *last*
          should be the keys for the items. Defaults to
          passthrough/the identity function.
       reverse (bool): Whether or not elements not explicitly ordered
          by *first* and *last* should be in reverse order or not.

    Returns a new list in sorted order.
    """
    first = first or []
    last = last or []
    key = key or (lambda x: x)
    seq = list(iterable)
    other = [x for x in seq if not ((first and key(x) in first) or (last and key(x) in last))]
    other.sort(key=key, reverse=reverse)

    if first:
        first = sorted([x for x in seq if key(x) in first], key=lambda x: first.index(key(x)))
    if last:
        last = sorted([x for x in seq if key(x) in last], key=lambda x: last.index(key(x)))
    return first + other + last


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
            links = ', '.join(['[%s](%s)' % (_format_url_name(name), url) for name, url
                               in soft_sorted(project.urls, key=lambda x: x[0], first=_URL_ORDER[:-1], last=_URL_ORDER[-1:])])

            line = tmpl.format(bullet=BULLET, name=project.name, links=links, desc=project.desc)
            if len(project.tags) > 1:
                other_tags = [t for t in project.tags if t != tag_entry.tag]
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


def main():
    plist = ProjectList.from_path('projects.yaml')
    plist.normalize()
    print(plist.to_yaml())

    topic_map = plist.get_projects_by_type('topic')
    topic_toc_text = format_tag_toc(topic_map)
    projects_by_topic = format_all_categories(topic_map)

    plat_map = plist.get_projects_by_type('platform')
    plat_toc_text = format_tag_toc(plat_map)
    projects_by_plat = format_all_categories(plat_map)

    context = {'TOPIC_TOC': topic_toc_text,
               'TOPIC_TEXT': projects_by_topic,
               'PLATFORM_TOC': plat_toc_text,
               'PLATFORM_TEXT': projects_by_plat,
               'TOTAL_COUNT': len(plist.project_list)}

    for filename in iter_find_files(TEMPLATES_PATH, '*.tmpl.md'):
        tmpl_text = open(filename).read()
        target_filename = os.path.split(filename)[1].replace('.tmpl', '')
        output_text = tmpl_text.format(**context)
        with atomic_save(target_filename) as f:
            f.write(output_text.encode('utf8'))

    return


if __name__ == '__main__':
    main()
