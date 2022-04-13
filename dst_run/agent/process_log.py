import logging
from dst_run.common.constants import FilePath


process_log = logging.getLogger(__name__)
formatter = logging.Formatter('[%(asctime)s] [%(threadName)s] %(message)s')
process_log.setLevel(logging.INFO)


def init_game_log():
    fh = logging.FileHandler(FilePath.GAME_LOG_PATH, 'w', encoding='utf-8')
    fh.setFormatter(formatter)
    fh.setLevel(logging.INFO)
    process_log.addHandler(fh)


init_game_log()





