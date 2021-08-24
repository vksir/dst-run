import logging
from time import strftime, localtime
from dst_run import LOG_FILE


def info(s, stdout=False):
    pass


def warning(s, stdout=False):
    pass


def error(s, stdout=False):
    pass


def log(s: str):
    with open(LOG_FILE, 'w+', encoding='utf-8') as f:
        f.write(strftime('[%Y-%m-%d-%H-%M-%S] {}\n'.format(s), localtime()))
