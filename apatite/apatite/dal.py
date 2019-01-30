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
from boltons.iterutils import soft_sorted

TOOLS_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_PATH = os.path.dirname(os.path.abspath(__file__)) + '/templates/'

# house = u"\u2302"
BULLET = '1.'
INDENT = ' ' * 4

PLIST_PREFACE_COMMENT = """\
Format of this file:

 - First we have the "tagsonomy", a tree of tags used to categorize the projects.
 - After that is "projects", a list of awesome projects

Each project has the following format:

 - name: Project Name
   repo_url: github or bitbucket or other web link to code
   wp_url: Wikipedia URL if there is one
   docs_url: URL to docs
   home_url: Home page if not one of the above
   tags: ["", ""]  # see full taxonomy elsewhere in this file
   desc: Handy project designed for handiness

Only the name, repo_url, tags, and description are required.

In the description, avoid references to Python, free/open-source, and
the app name itself, since those are already present/implied by being
on the list.  """


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
        ret.yaml_set_start_comment('\n' + PLIST_PREFACE_COMMENT + '\n\n')
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

        ret['projects'] = plist
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
