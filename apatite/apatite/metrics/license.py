import datetime
import glom
import json
import subprocess
import time
from apatite.cli import ProcessResult

DETECT_CMD = 'license-detector'

required_cmds = {DETECT_CMD:
                 'Download from: https://github.com/src-d/go-license-detector/releases,'
                 ' rename to "license-detector", place it on your PATH,'
                 ' and make it executable.'}

def collect(project, repo_dir):

    started = datetime.datetime.utcnow()
    proc = subprocess.Popen([DETECT_CMD, repo_dir, '--format', 'json'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    proc_res = ProcessResult(returncode=proc.returncode,
                             stdout=stdout.decode('utf8'),
                             stderr=stderr,
                             start_time=started,
                             end_time=datetime.datetime.utcnow())
    output_json = json.loads(proc_res.stdout)
    possible_licenses = glom.glom(output_json, glom.Coalesce('0.matches'), default=[])
    # sort and set into descending order
    possible_licenses = sorted(possible_licenses, key=lambda x: x['confidence'] * -1)
    num_possible_licenses = len(possible_licenses)

    if num_possible_licenses > 3:
        possible_licenses = possible_licenses[:3]

    return {'licenses': possible_licenses, 'total_detected_licenses': num_possible_licenses}
