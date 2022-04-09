import abc
from collections import UserDict
from dst_run.common.data_lib import DataLib


class BaseConf(abc.ABC, UserDict):
    def __init__(self, data: dict):
        super().__init__(data)
        self._set_default()

    @abc.abstractmethod
    def deploy(self) -> None:
        pass

    @abc.abstractmethod
    def load(self) -> None:
        pass

    def _set_default(self):
        DataLib.set_default(self, self._default)

    @property
    @abc.abstractmethod
    def _default(self) -> dict:
        pass
