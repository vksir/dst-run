import abc
import queue
from typing import Union
from typing import Any


class BaseQueue(abc.ABC):
    def __init__(self):
        self._que = queue.Queue()

    @abc.abstractmethod
    def produce(self, *args, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def consume(self) -> Union[Any, None]:
        pass
