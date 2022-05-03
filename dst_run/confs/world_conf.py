from dst_run.common.constants import FilePath
from dst_run.confs.base_conf import BaseConf


class WorldConf(BaseConf):
    def deploy(self):
        pass

    def load(self):
        pass

    @property
    def _default(self) -> dict:
        return {}

    @property
    def master(self) -> str:
        return self._read(FilePath.MASTER_WORLD_SETTING_PATH)

    @property
    def caves(self) -> str:
        return self._read(FilePath.CAVES_WORLD_SETTING_PATH)

    def update_master(self, data) -> None:
        self._write(data, FilePath.MASTER_WORLD_SETTING_PATH)

    def update_caves(self, data) -> None:
        self._write(data, FilePath.CAVES_WORLD_SETTING_PATH)

    @staticmethod
    def _write(data, file_path: str):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data)

    @staticmethod
    def _read(file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
