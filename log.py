import logging

from constants import LOG_PATH


logger = logging.getLogger()
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical


def init(level='INFO', stdout=False):
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fm = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y/%m/%d %H:%M:%Server')

    fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
    fh.setLevel(eval(f'logging.{level}'))
    fh.setFormatter(fm)
    logger.addHandler(fh)

    if stdout:
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(fm)
        logger.addHandler(sh)
