# -*- encoding:utf-8 -*-
import os

import attr
from ruamel import yaml
from boltons.dictutils import OMD

TOOLS_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/templates/'

house = u"\u2302"


@attr.s(frozen=True)
class TagEntry(object):
    tag = attr.ib()
    tag_type = attr.ib()
    title = attr.ib()
    subtags = attr.ib(default=None, repr=False)
    supertag = attr.ib(default=None, repr=False)
    fq_tag = attr.ib(default=None)


def _unwrap_dict(d):
    if not len(d) == 1:
        raise ValueError('expected single-member dict')
    return list(d.items())[0]


class ProjectList(object):
    def __init__(self, project_list, tagsonomy):
        self.project_list = project_list
        self.tagsonomy = tagsonomy

        self.tag_registry = OMD()
        self.tag_alias_map = OMD()
        for tag in self.tagsonomy['topic']:
            self.register_tag('topic', tag)

    @classmethod
    def from_path(cls, path):
        data = yaml.safe_load(open(path))
        return cls(data['projects'], data['tagsonomy'])

    def register_tag(self, tag_type, tag_entry, tag_path=None):
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

        if not tag_path:
            ret = TagEntry(**tag_entry)
        else:
            fq_tag = '.'.join(tag_path + (tag,))
            ret = TagEntry(supertag=tag_path, fq_tag=fq_tag, **tag_entry)
            # also register the fq version
            self.tag_registry[fq_tag] = attr.evolve(ret, tag=fq_tag, fq_tag=None)

        self.tag_registry[tag] = ret
        return ret

    def get_projects_by_topic(self):
        ret = OMD()
        for tag, tag_entry in self.tag_registry.items():
            if tag_entry.tag_type != 'topic':
                continue
            ret[tag_entry] = []
            for project in self.project_list:
                if tag in project.get('tags', []):
                    ret[tag_entry].append(project)
        return ret



def main():
    plist = ProjectList.from_path('projects.yaml')
    readme_tmpl = open(TEMPLATES_PATH + '/README.tmpl.md').read()
    print(readme_tmpl)
    from pprint import pprint
    pprint(plist.tag_registry.todict())
    pprint(plist.get_projects_by_topic(), compact=True, width=120)
    import pdb;pdb.set_trace()


if __name__ == '__main__':
    main()
