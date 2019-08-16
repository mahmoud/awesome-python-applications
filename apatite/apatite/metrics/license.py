import re
import json
import datetime
import subprocess
from collections import Counter

import glom

from apatite.utils import run_cap

DETECT_CMD = 'license-detector'

required_cmds = {DETECT_CMD:
                 'Download from: https://github.com/src-d/go-license-detector/releases,'
                 ' rename to "license-detector" (if need be), place it on your PATH,'
                 ' and make it executable.'}

# missing = "other"
LICENSE_MAP = {
    'AFL-3.0': 'AFL',
    'AGPL-1.0': 'AGPL',
    'AGPL-3.0': 'AGPL',
    'AGPL-3.0-only': 'AGPL',
    'AGPL-3.0-or-later': 'AGPL',
    'Apache-2.0': 'Apache-2.0',
    'BSD-2-Clause': 'BSD-2',
    'BSD-2-Clause-FreeBSD': 'BSD-2',
    'BSD-2-Clause-NetBSD': 'BSD-2',
    'BSD-3-Clause': 'BSD-3',
    'BSD-3-Clause-Clear': 'BSD-3',
    'BSD-3-Clause-No-Nuclear-License-2014': 'BSD-3',
    'BSD-4-Clause': 'BSD-3',  # sure it exists, but not here
    'BSD-Source-Code': 'BSD-3',
    'CDDL-1.0': 'CDDL',
    'CDDL-1.1': 'CDDL',
    'GPL-2.0': 'GPL v2',
    'GPL-2.0-only': 'GPL v2',
    'GPL-2.0-or-later': 'GPL v2',
    'GPL-3.0-only': 'GPL v3',
    'GPL-3.0-or-later': 'GPL v3',
    'ISC': 'ISC',
    'LGPL-2.0+': 'LGPL v2',
    'LGPL-2.0-only': 'LGPL v2',
    'LGPL-2.0-or-later': 'LGPL v2',
    'LGPL-2.1': 'LGPL v2',
    'LGPL-2.1-only': 'LGPL v2',
    'LGPL-2.1-or-later': 'LGPL v2',
    'LGPL-3.0-only': 'LGPL v3',
    'LGPL-3.0-or-later': 'LGPL v3',
    'MIT': 'MIT',
    'MIT-feh': 'MIT',
    'MPL-1.1': 'MPL',
    'MPL-2.0': 'MPL',
    'MPL-2.0-no-copyleft-exception': 'MPL',
    'Unlicense': 'Unlicense',
    'deprecated_AGPL-3.0': 'AGPL  ',
    'deprecated_GPL-2.0': 'GPL v2',
    'deprecated_GPL-2.0+': 'GPL v2',
    'deprecated_GPL-3.0': 'GPL v3',
    'deprecated_GPL-3.0+': 'GPL v3',
    'deprecated_LGPL-2.0': 'LGPL v2',
    'deprecated_LGPL-2.0+': 'LGPL v2',
    'deprecated_LGPL-2.1': 'LGPL v2',
    'deprecated_LGPL-2.1+': 'LGPL v2',
    'deprecated_LGPL-3.0': 'LGPL v3',
    'deprecated_LGPL-3.0+': 'LGPL v3'}


# OSL: True
GROUP_HEREDITARY_MAP = {'AFL': False,
                        'AGPL': True,
                        'Apache': True,
                        'BSD': False,
                        'CDDL': False,
                        'GPL': True,
                        'ISC': True,
                        'LGPL': True,
                        'MIT': False,
                        'MPL': True,
                        'Unlicense': True}


'''
Too many false positives of these:
 'CC-BY-3.0': 'CC',
 'CC-BY-4.0': 'CC',
 'CC0-1.0': 'CC0',
'''


def collect(plist, project, repo_dir):
    ret = {}
    proc_res = run_cap([DETECT_CMD, repo_dir, '--format', 'json'])
    output_json = json.loads(proc_res.stdout)
    possible_licenses = glom.glom(output_json, '0.matches', default=[])
    # sort and set into descending order
    possible_licenses = sorted(possible_licenses, key=lambda x: x['confidence'], reverse=True)[:3]
    norm_licenses = []
    for pl in possible_licenses:
        if pl['confidence'] < 0.9:
            continue
        elif pl['license'] not in LICENSE_MAP:
            continue
        norm_licenses.append((LICENSE_MAP[pl['license']], round(pl['confidence'], 3)))

    if not norm_licenses or len(norm_licenses) > 3:
        ret['license'] = 'Other'  # not enough consensus on a known license
    else:
        sorted(norm_licenses, key=lambda x: x[1], reverse=True)
        if len(norm_licenses) < 3:
            ret['license'] = norm_licenses[0][0]
        else:
            most_common = Counter([x[0] for x in norm_licenses]).most_common(1)[0][0]
            ret['license'] = most_common

    group = re.split('\W+', ret['license'])[0]
    ret['license_group'] = group
    ret['hereditary'] = GROUP_HEREDITARY_MAP.get(group)

    return ret
