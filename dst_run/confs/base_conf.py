import abc
from typing import Union
from collections import UserDict


class BaseConf(abc.ABC, UserDict):
    def __init__(self, data: Union[None, dict]):
        if data is None:
            data = self._get_init_data()
        super().__init__(data)

    @abc.abstractmethod
    def deploy(self) -> None:
        pass

    @abc.abstractmethod
    def load(self) -> None:
        pass

    @abc.abstractmethod
    def _get_init_data(self):
        pass

