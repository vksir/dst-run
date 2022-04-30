import os
import uuid
from typing import List
from dst_run.common.constants import FilePath
from dst_run.confs.base_conf import BaseConf


class CommonConf(BaseConf):
    def deploy(self):
        pass

    def load(self):
        self._load_version()

    @property
    def _default(self) -> dict:
        version = self._load_version()
        return {
            'nickname': '',
            'uuid': str(uuid.uuid4()),
            'enable_64bit': True,
            'enable_caves': True,
            'version': version,
            'proxy': '',
            'authenticate': {
                'enable': True,
                'host': '127.0.0.1',
                'port': 12599,
                'ip_whitelist': ['127.0.0.1'],
            },
            'report': {
                'host': '127.0.0.1',
                'port': 5701,
                'level': 'debug'
            }
        }

    @property
    def nickname(self):
        return self['nickname']

    @property
    def uuid(self):
        return self['uuid']

    @property
    def authenticate_enable(self) -> bool:
        return self['authenticate']['enable']

    @property
    def authenticate_host(self) -> str:
        return self['authenticate']['host']

    @property
    def authenticate_port(self) -> int:
        return self['authenticate']['port']

    @property
    def authenticate_ip_whitelist(self) -> List[str]:
        return self['authenticate']['ip_whitelist']

    @property
    def enable_64bit(self) -> bool:
        return self.get('enable_64bit', True)

    @property
    def enable_caves(self) -> bool:
        return self.get('enable_caves', True)

    @property
    def version(self) -> str:
        return self.get('version', '')

    @property
    def report_host(self) -> str:
        return self['report']['host']

    @property
    def report_port(self) -> int:
        return self['report']['port']

    @property
    def report_level(self) -> str:
        return self['report']['level']

    @property
    def proxy(self) -> str:
        return self['proxy']

    @staticmethod
    def _load_version():
        version_path = f'{FilePath.DST_DIR}/version.txt'
        if not os.path.exists(version_path):
            return ''
        with open(version_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
