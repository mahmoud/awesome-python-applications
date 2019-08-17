# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import io
import os
import copy

import attr
import schema
from glom import glom, T, Coalesce
from ruamel.yaml import YAML, round_trip_load
from ruamel.yaml.comments import CommentedMap
from boltons.dictutils import OMD
from boltons.fileutils import iter_find_files, atomic_save
from boltons.iterutils import soft_sorted, redundant, unique
from boltons.strutils import slugify
from hyperlink import parse as url_parse

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


def parse_valid_url(url, schemes=None):
    url_obj = url_parse(url)
    url_obj = url_obj.normalize()

    assert url_obj.scheme
    if schemes is not None:
        assert url_obj.scheme in schemes
    assert url_obj.host

    return url_obj


def parse_valid_web_url(url):
    return parse_valid_url(url, schemes=('http', 'https'))


_PROJECT_SCHEMA = schema.Schema(
    {'name': str,
     schema.Optional(schema.Regex('\w+_url')): parse_valid_url,
     'repo_url': parse_valid_web_url,
     'desc': str,
     'tags': tuple},
    ignore_extra_keys=False)


class ApatiteError(Exception):
    pass


class DuplicateProjectError(ApatiteError):
    pass


class ProjectValidationError(ApatiteError):
    @classmethod
    def from_pdict_error(cls, pdict, error):
        msg = '%s while validating project' % error

        name = pdict.get('name')
        if name is not None:
            msg += ' %r' % name

        line = glom(pdict, T.lc.line, default=None)
        if line is not None:
            msg += ' on line %r' % line

        if name is None and line is None:
            msg += ' %r' % pdict

        ret = cls(msg)
        ret.pdict = pdict
        ret.error = error
        return ret


class ProjectListError(ApatiteError):
    @classmethod
    def from_errors(cls, errors):
        msg = 'encountered %s errors in the project list:' % len(errors)
        msg += '\n'.join([''] + ['  - ' + repr(e) for e in errors])
        ret = cls(msg)
        ret.errors = errors
        return ret


def validate_project_dict(pdict):
    try:
        return _PROJECT_SCHEMA.validate(pdict)
    except schema.SchemaError as se:
        raise ProjectValidationError.from_pdict_error(pdict, se)


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
    _tags = attr.ib(default=())
    urls = attr.ib(default=())
    _orig_data = attr.ib(default=None, repr=False, cmp=False)

    @property
    def name_slug(self):
        return slugify(self.name)

    @property
    def repo_url(self):
        for name, url in self.urls:
            if name == 'repo':
                return url
        return None

    @property
    def author(self):
        if self.repo_url.host != 'github.com':
            return None
        return self.repo_url.path[0]

    @property
    def repo_name(self):
        if self.repo_url.host != 'github.com':
            return None
        return self.repo_url.path[1]

    @property
    def clone_info(self):
        for name, url in self.urls:
            if name == 'clone':
                vcs, _, scheme = url.scheme.rpartition('+')
                clone_url = url.replace(scheme=scheme)
                return (vcs, clone_url)

        repo_url = self.repo_url

        if repo_url.host == 'github.com' or 'gitlab.' in repo_url.host:  # covers gitlab.gnome.org, too
            return ('git', repo_url.replace(path=repo_url.path[:-1] + (repo_url.path[-1] + '.git',)))
        elif repo_url.path[-1].endswith('.git'):
            return ('git', repo_url)
        elif repo_url.host == 'bitbucket.org':
            return ('hg', repo_url.replace(path=(repo_url.path[0], repo_url.path[1])))
        elif repo_url.host == 'code.launchpad.net':
            return ('bzr', 'lp:' + repo_url.path[0])
        return (None, None)

    @classmethod
    def from_dict(cls, d):
        validate_project_dict(d)
        kwargs = dict(d)
        tags = tuple([slugify(t) for t in kwargs.get('tags', ())])
        dupe_groups = redundant(tags, groups=True)
        if dupe_groups:
            raise ProjectValidationError('duplicate tags in project %r: %r'
                                         % (kwargs['name'], dupe_groups))
        kwargs['tags'] = tags
        cur_urls = ()
        for k in list(kwargs):
            if not k.endswith('_url'):
                continue
            val = kwargs.pop(k)
            val = parse_valid_url(val)
            cur_urls += ((k[:-4], val),)
            kwargs['urls'] = cur_urls
        kwargs['orig_data'] = d
        return cls(**kwargs)

    def to_dict(self):
        # deepcopy necessary to maintain comments
        ret = copy.deepcopy(self._orig_data) if self._orig_data else CommentedMap()
        # print(to_yaml(ret), end='')
        ret['name'] = self.name
        ret['desc'] = self.desc
        ret['tags'] = self._tags
        for url_type, url in self.urls:
            ret[url_type + '_url'] = str(url)
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

        errors = []
        for project in project_list:
            new_tags = tuple(soft_sorted(project.get('tags', []), first=self.tag_registry.keys()))
            project['tags'] = new_tags
            try:
                project_obj = Project.from_dict(project)
            except ApatiteError as ae:
                errors.append(ae)
                continue
            self.project_list.append(project_obj)

        dupe_groups = redundant(self.project_list,
                                key=lambda p: slugify(p.name),
                                groups=True)
        dupe_groups += redundant(self.project_list,
                                 key=lambda p: p.repo_url,
                                 groups=True)
        dupe_groups = unique([tuple(dg) for dg in dupe_groups])
        for group in dupe_groups:
            dpe = DuplicateProjectError('ambiguous or duplicate projects: %r' %
                                        [p.name for p in group])
            errors.append(dpe)

        if errors:
            raise ProjectListError.from_errors(errors)
        return

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
            topic_tags = [t for t in p._tags
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
            topic_tags = [t for t in project._tags
                          if t in self.tag_registry
                          and self.tag_registry[t].tag_type == 'topic']
            first_topic = topic_tags[0] if topic_tags else 'misc'  # TODO: might change to uncategorized in future
            first_topic_idx = tag_list.index(first_topic)
            return (first_topic_idx, project.name.lower())

        project_list = []
        for project in sorted(self.project_list, key=plist_sort_key):
            if not project.desc[-1:] in ').!':
                project = attr.evolve(project, desc=project.desc + '.')

            cleaned_urls = []
            for url_name, url in project.urls:
                # strip off trailing slashes from all urls
                new_path = tuple([segm for segm in url.path if segm != ''])
                cleaned_urls.append((url_name, url.replace(path=new_path)))
            project = attr.evolve(project, urls=cleaned_urls)

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
                if tag in project._tags:
                    ret[tag_entry].append(project)
            ret[tag_entry].sort(key=lambda x: x.name.lower())
        return ret


@attr.s
class ResultFile(object):
    entries = attr.ib()
