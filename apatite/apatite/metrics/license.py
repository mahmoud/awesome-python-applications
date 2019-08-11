import datetime
import json
import subprocess
import time
from apatite.cli import ProcessResult

instr = ('Download from: https://github.com/src-d/go-license-detector/releases,',
         ' rename to "license-detector", place it on your PATH,'
         ' and make it executable.')

CMD_NAME = 'license-detector'

required_cmds = {'name': CMD_NAME, 'instructions': instr}

def collect(project, repo_dir):

    started = datetime.datetime.utcnow()
    proc = subprocess.Popen([CMD_NAME, repo_dir, '--format', 'json'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    proc_res = ProcessResult(returncode=proc.returncode,
                             stdout=stdout.decode('utf8'),
                             stderr=stderr,
                             start_time=started,
                             end_time=datetime.datetime.utcnow())
    possible_licenses = json.loads(proc_res.stdout)
    try:
        lic = possible_licenses[0]['matches'][0]['license']
    except KeyError:
        lic = possible_licenses[0]['error']
    return {'license': lic}

# TOOD
# add top three licenses and confidences
# add total licenses detected as number
