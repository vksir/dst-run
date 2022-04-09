import os
from typing import Union
import yaml
from dst_run.common.constants import FilePath
from dst_run.common.log import log
from dst_run.confs.base_conf import BaseConf
from dst_run.confs.common_conf import CommonConf
from dst_run.confs.cluster_conf import ClusterConf
from dst_run.confs.room_conf import RoomConf
from dst_run.confs.world_conf import WorldConf
from dst_run.confs.mod_conf import ModConf


__all__ = ['CONF']


class Confs(BaseConf):
    def __init__(self):
        data = self._read()
        data = data or {}
        super().__init__(data)

        self.common = CommonConf(self['common'])
        self.cluster = ClusterConf(self['cluster'])
        self.room = RoomConf(self['room'])
        self.world = WorldConf(self['world'])
        self.mod = ModConf(self['mod'])

        self.save()

    def deploy(self) -> None:
        self.common.deploy()
        self.cluster.deploy()
        self.room.deploy()
        self.world.deploy()
        self.mod.deploy()

    def load(self) -> None:
        self.common.load()
        self.cluster.load()
        self.room.load()
        self.world.load()
        self.mod.load()
        self.save()

    @property
    def _default(self) -> dict:
        return {
            'common': {},
            'cluster': {},
            'room': {},
            'world': {},
            'mod': {}
        }

    @staticmethod
    def _read() -> Union[None, dict]:
        if not os.path.exists(FilePath.CFG_PATH):
            return None
        try:
            with open(FilePath.CFG_PATH, 'r', encoding='utf-8') as f:
                cfg = yaml.load(f, Loader=yaml.Loader)
        except Exception as e:
            log.error(f'read cfg failed: e={e}')
            return None
        return cfg

    def read(self) -> None:
        data = self._read()
        if data is not None:
            self.data = data

    @staticmethod
    def _save(data: dict) -> None:
        with open(FilePath.CFG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(data, f)

    def save(self):
        self['common'] = dict(self.common)
        self['cluster'] = dict(self.cluster)
        self['room'] = dict(self.room)
        self['world'] = dict(self.world)
        self['mod'] = dict(self.mod)
        self._save(dict(self))


CONF = Confs()
