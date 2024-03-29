import time
import threading
from typing import Union
from dst_run.common.log import log
from dst_run.message_queue.base_queue import BaseQueue
from dst_run.reporter.reporter import REPORTER

__all__ = ['MSG_QUEUE']


class Msg:
    def __init__(self, process: str, msg: str):
        self.process = process
        self.msg = msg


class MsgQueue(BaseQueue):
    def produce(self, process: str, msg: str) -> None:
        self._que.put(Msg(process, msg))

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
                REPORTER.report_raw_message(msg.process, msg.msg)
                continue
            time.sleep(1)


MSG_QUEUE = MsgQueue()
msg_handler = MsgHandler(daemon=True)
msg_handler.start()
