import re
from dst_run.common.constants import FilePath
from dst_run.confs.base_conf import BaseConf


class WorldConf(BaseConf):
    def deploy(self):
        self._deploy(self.master, FilePath.MASTER_WORLD_SETTING_PATH)
        self._deploy(self.caves, FilePath.CAVES_WORLD_SETTING_PATH)

    def load(self):
        data = self._load(FilePath.MASTER_WORLD_SETTING_PATH)
        self['master'] = data
        data = self._load(FilePath.CAVES_WORLD_SETTING_PATH)
        self['caves'] = data

    @property
    def _default(self) -> dict:
        return {
            'master': {},
            'caves': {}
        }

    @property
    def master(self) -> dict:
        return self['master']

    @property
    def caves(self) -> dict:
        return self['caves']

    def update_master(self, data) -> None:
        self['master'].update(data)

    def update_caves(self, data) -> None:
        self['caves'].update(data)

    @staticmethod
    def _deploy(data: dict, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        for key, value in data.items():
            content = re.sub(r'%s=".*?"' % key, f'{key}="{value}"', content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def _load(file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        data = re.search(r'overrides=\{.*?\}', content, re.S).group()
        data = re.findall(r'([^\s]+?)="([^\s]+?)"', data)
        data = {item[0]: item[1] for item in data}
        return data
