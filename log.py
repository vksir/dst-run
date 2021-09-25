import logging

from constants import LOG_PATH


__all__ = ['log']


def init(level=logging.INFO):
    global log
    log = logging.getLogger()
    log.setLevel(level)
    fm = logging.Formatter('%(asctime)s [%(levelname)s][%(filename)s] %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

    fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fm)
    log.addHandler(fh)


log = logging.getLogger()
init(logging.INFO)
