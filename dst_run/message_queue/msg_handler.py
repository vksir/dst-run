import time
import threading
from typing import Union
from dst_run.common.log import log
from dst_run.message_queue.base_queue import BaseQueue
from dst_run.reporter.reporter import REPORTER

__all__ = ['MSG_QUEUE']


class Msg:
    def __init__(self, msg: str):
        self.msg = msg


class MsgQueue(BaseQueue):
    def produce(self, msg: str) -> None:
        self._que.put(Msg(msg))

    def consume(self) -> Union[Msg, None]:
        if self._que.empty():
            return None
        return self._que.get()


class MsgHandler(threading.Thread):
    def run(self) -> None:
        log.info('start msg handler thread')
        while True:
            msg = MSG_QUEUE.consume()
            if msg is not None:
                REPORTER.deal_with_msg(msg)
                continue
            time.sleep(1)


MSG_QUEUE = MsgQueue()
msg_handler = MsgHandler()
msg_handler.start()
