import logging

from dst_run import LOG_FILE


logger = logging.getLogger()


def init():
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fm = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(fm)
    logger.addHandler(sh)

    fh = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fm)
    logger.addHandler(fh)


def debug(s):
    logger.debug(s)


def info(s):
    logger.info(s)


def warning(s):
    logger.error(s)


def error(s):
    logger.error(s)


def critical(s):
    logger.critical(s)
