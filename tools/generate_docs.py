# -*- encoding:utf-8 -*-
import os
from ruamel import yaml
from boltons.dictutils import OMD

TOOLS_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/templates/'

house = u"\u2302"


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
            self.register_tag(tag)

    @classmethod
    def from_path(cls, path):
        data = yaml.safe_load(open(path))
        return cls(data['projects'], data['tagsonomy'])

    def register_tag(self, tag_entry, tag_path=None):
        if isinstance(tag_entry, str):
            tag, tag_entry = tag_entry, {}
        else:
            tag, tag_entry = _unwrap_dict(tag_entry)
            tag_entry = dict(tag_entry)

        if not tag_entry.get('title'):
            tag_entry["title"] = tag.replace('_', ' ').title()

        for subtag_entry in tag_entry.pop('subtags', []):
            self.register_tag(subtag_entry,
                              tag_path=[tag] if not tag_path else tag_path + [tag])

        if tag_path:
            tag_entry['super'] = tag_path
            fq_tag = '.'.join(tag_path + [tag])
            self.tag_registry[fq_tag] = dict(tag_entry)
            tag_entry['fq_tag'] = fq_tag

        self.tag_registry[tag] = dict(tag_entry)

    def get_projects_by_topic(self):
        ret = OMD()
        topic_list = self.tagsonomy['topic']
        for project in self.project_list:
            pass


def main():
    plist = ProjectList.from_path('projects.yaml')
    readme_tmpl = open(TEMPLATES_PATH + '/README.tmpl.md').read()
    print(readme_tmpl)
    from pprint import pprint
    pprint(plist.tag_registry.todict())
    import pdb;pdb.set_trace()


if __name__ == '__main__':
    main()
