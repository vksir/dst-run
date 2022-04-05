import os
from typing import List
from dst_run.common.constants import FilePath
from dst_run.confs.base_conf import BaseConf


class CommonConf(BaseConf):
    def deploy(self):
        pass

    def load(self):
        self._load_version()

    def _get_init_data(self):
        version = self._load_version()
        return {
            'ip_whitelist': [],
            'enable_64bit': True,
            'enable_caves': True,
            'version': version
        }

    @property
    def ip_whitelist(self) -> List[str]:
        ip_whitelist = self['ip_whitelist']
        ip_whitelist.append('127.0.0.1')
        return ip_whitelist

    @property
    def enable_64bit(self) -> bool:
        return self['enable_64bit']

    @property
    def enable_caves(self) -> bool:
        return self['enable_caves']

    @property
    def version(self) -> str:
        return self['version']

    @staticmethod
    def _load_version():
        version_path = f'{FilePath.DST_DIR}/version.txt'
        if not os.path.exists(version_path):
            return ''
        with open(version_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
