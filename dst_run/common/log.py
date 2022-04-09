import os
import logging

from dst_run.common import constants
from dst_run.common.constants import FilePath


log = logging.getLogger(__name__)
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(filename)s] %(message)s')
log.setLevel(logging.DEBUG)


def init_path():
    for path_name in dir(constants):
        path = getattr(constants, path_name)
        if (not path_name.endswith('HOME') and not path_name.endswith('DIR')) \
                or os.path.exists(path):
            continue
        os.system(f'mkdir -p {path}')


def init_log():
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    sh.setLevel(logging.DEBUG)
    fh = logging.FileHandler(FilePath.LOG_PATH, 'w', encoding='utf-8')
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    log.addHandler(sh)
    log.addHandler(fh)


init_path()
init_log()





