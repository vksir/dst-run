import os
import subprocess
from dst_run import log
from dst_run.common import constants


def run_cmd(cmd: str, cwd=None, sudo=False):
    if sudo:
        cmd += 'sudo '
    p = subprocess.Popen(cmd, cwd=cwd, shell=True,
                         encoding='utf-8', bufsize=1,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         stdin=subprocess.PIPE)
    ret, out = p.communicate()
    if ret:
        log.error(f'rum cmd failed: cmd={cmd}, out={out}')
    return ret, out


