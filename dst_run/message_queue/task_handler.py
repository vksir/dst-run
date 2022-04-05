import time
import threading
import queue
from typing import Union
from typing import Callable
from dst_run.common.log import log
from dst_run.message_queue.base_queue import BaseQueue


__all__ = ['TASK_QUEUE']


class Task:
    def __init__(self, func: Callable, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs


class TaskQueue(BaseQueue):
    def produce(self, func: Callable, *args, **kwargs) -> None:
        log.info(f'produce task: func={func.__name__}, args={args}, kwargs={kwargs}')
        self._que.put(Task(func, *args, **kwargs))

    def consume(self) -> Union[Task, None]:
        if self._que.empty():
            return None
        task = self._que.get()
        log.info(f'consume task: func={task.func.__name__}, args={task.args}, kwargs={task.kwargs}')
        return task


class TaskHandler(threading.Thread):
    def run(self) -> None:
        log.info('start task handler thread')
        while True:
            task = TASK_QUEUE.consume()
            if task is not None:
                task.func(*task.args, **task.kwargs)
                continue
            time.sleep(1)


TASK_QUEUE = TaskQueue()
task_handler = TaskHandler()
task_handler.start()
