import os
import re
import time
import abc
from typing import List, Union
from configparser import ConfigParser
from collections import UserDict
import yaml
from dst_run.common.constants import FilePath
from dst_run.common.constants import Constants
from dst_run.common.data_lib import DataLib
from dst_run.common.log import log
from dst_run.common.utils import run_cmd


class BaseCfg(UserDict):
    def __init__(self):
        super().__init__()
        if not os.path.exists(FilePath.CFG_PATH):
            self.data = {}
            self.save_cfg()
        self.read_cfg()

    def read_cfg(self):
        with open(FilePath.CFG_PATH, 'r', encoding='utf-8') as f:
            cfg = yaml.load(f, Loader=yaml.Loader)
            self.data = cfg

    def save_cfg(self):
        with open(FilePath.CFG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(self.data, f, sort_keys=False)


class BaseCfgHandler(abc.ABC, UserDict):
    @abc.abstractmethod
    def __init__(self, base_cfg: BaseCfg, key: str):
        self._base_cfg = base_cfg
        self._key = key
        if key not in base_cfg:
            self.init()

        # 初始化传值，防止 self.data = {}
        super().__init__(self._base_cfg[self._key])

    def init(self):
        self._base_cfg[self._key] = self._get_init_data()
        self._base_cfg.save_cfg()

    @abc.abstractmethod
    def deploy(self) -> None:
        pass

    @abc.abstractmethod
    def load(self) -> None:
        pass

    @abc.abstractmethod
    def _get_init_data(self):
        pass

    @property
    def data(self):
        return self._base_cfg[self._key]

    @data.setter
    def data(self, value):
        self._base_cfg[self._key] = value


class CommonCfgHandler(BaseCfgHandler):
    def __init__(self, base_cfg: BaseCfg):
        super().__init__(base_cfg, key='common')

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

    def get_ip_whitelist(self):
        ip_whitelist = self['ip_whitelist']
        ip_whitelist.append('127.0.0.1')
        return ip_whitelist

    def get_enable_64bit(self):
        return self['enable_64bit']

    def get_enable_caves(self):
        return self['enable_caves']

    def get_version(self):
        return self['version']

    @staticmethod
    def _load_version():
        version_path = f'{FilePath.DST_DIR}/version.txt'
        if not os.path.exists(version_path):
            return ''
        with open(version_path, 'r', encoding='utf-8') as f:
            return f.read().strip()


class ClusterCfgHandler(BaseCfgHandler):
    def __init__(self, base_cfg: BaseCfg):
        super().__init__(base_cfg, key='cluster')

    def deploy(self):
        self.create_cluster_by_template_cluster(force=False)
        self._deploy_admins()
        self._deploy_token()

    def load(self):
        self.create_cluster_by_template_cluster(force=False)

    def _get_init_data(self):
        token = input('Please input your token: ')
        return {
            'used_cluster': 'Cluster_1',
            'used_template': 'default',
            'token': token,
            'admins': []
        }

    def _deploy_admins(self):
        admin_data = '\n'.join(self['admins'])
        with open(FilePath.ADMINS_PATH, 'w', encoding='utf-8') as f:
            f.write(admin_data)

    def _deploy_token(self):
        with open(FilePath.CLUSTER_TOKEN_PATH, 'w', encoding='utf-8') as f:
            f.write(self['token'])

    def list_template_clusters(self):
        pass

    def list_backup_clusters(self):
        ret, out = run_cmd(f'ls {FilePath.CLUSTERS_BACKUP_DIR}')
        if ret:
            return None
        clusters = [i.replace('.tar.gz', '') for i in out.split()]
        clusters.append(self['used_cluster'])
        return clusters

    def create_cluster_by_template_cluster(self, force=True):
        cluster_path = f'{FilePath.CLUSTERS_DIR}/{FilePath.CLUSTER_NAME}'
        if not force and os.path.exists(cluster_path):
            return

        template = self['used_template']
        default_template_path = f'{FilePath.TEMPLATE_DIR}/{template}'
        custom_template_path = f'{FilePath.CUSTOM_TEMPLATE_DIR}/{template}'
        if os.path.exists(default_template_path):
            template_path = default_template_path
        elif os.path.exists(custom_template_path):
            template_path = custom_template_path
        else:
            log.error(f'template not found: template={template}')
            template_path = f'{FilePath.TEMPLATE_DIR}/default'

        self.create_backup_cluster_by_cluster()
        run_cmd(f'rm -rf {cluster_path}')
        run_cmd(f'cp -rf {template_path} {cluster_path}')

    def create_cluster_by_backup_cluster(self):
        pass

    def create_template_cluster_by_cluster(self):
        pass

    def create_template_cluster_by_upload(self):
        pass

    @staticmethod
    def create_backup_cluster_by_cluster():
        cluster_path = f'{FilePath.CLUSTERS_DIR}/{FilePath.CLUSTER_NAME}'
        if not os.path.exists(cluster_path):
            return
        file_name = time.strftime(f'%Y-%m-%d_%H-%M-%S', time.localtime())
        run_cmd(f'tar -czvf {FilePath.CLUSTERS_BACKUP_DIR}/{file_name}.tar.gz {FilePath.CLUSTER_NAME}',
                cwd=FilePath.CLUSTERS_DIR)

    def create_backup_cluster_by_upload(self):
        pass

    def delete_template_cluster(self):
        pass

    @staticmethod
    def delete_backup_cluster(cluster_name: str):
        backup_cluster_path = f'{FilePath.CLUSTERS_BACKUP_DIR}/{cluster_name}.tar.gz'
        if not os.path.exists(backup_cluster_path):
            return
        run_cmd(f'rm -rf {backup_cluster_path}')

    def rename_template_cluster(self):
        pass

    @staticmethod
    def rename_backup_cluster(cluster_name: str, new_name: str):
        backup_cluster_path = f'{FilePath.CLUSTERS_BACKUP_DIR}/{cluster_name}.tar.gz'
        if not os.path.exists(backup_cluster_path):
            return
        new_backup_cluster_path = f'{FilePath.CLUSTERS_BACKUP_DIR}/{new_name}.tar.gz'
        run_cmd(f'mv -f {backup_cluster_path} {new_backup_cluster_path}')


class RoomCfgHandler(BaseCfgHandler):
    def __init__(self, base_cfg: BaseCfg):
        super().__init__(base_cfg, key='room')

    def deploy(self):
        room_setting = ConfigParser()
        with open(FilePath.ROOM_SETTING_PATH, 'r', encoding='utf-8') as f:
            room_setting.read_file(f)
        for section_key, section in self.items():
            for key, value in section.items():
                if isinstance(value, int):
                    value = str(value)
                room_setting[section_key][key] = value
        with open(FilePath.ROOM_SETTING_PATH, 'w', encoding='utf-8') as f:
            room_setting.write(f)

    def load(self):
        pass

    def _get_init_data(self):
        return {
            'GAMEPLAY': {
                'game_mode': 'endless',
                'max_players': '6',
                'pvp': 'false'
            },
            'NETWORK': {
                'cluster_name': 'DST_RUN',
                'cluster_password': '6666',
                'cluster_description': 'Just Have Fun'
            }
        }

    def get_room(self) -> dict:
        return dict(self)

    def update(self, room_data: dict, *args, **kwargs) -> None:
        DataLib.deep_update(self.data, room_data)


class WorldCfgHandler(BaseCfgHandler):
    def __init__(self, base_cfg: BaseCfg):
        super().__init__(base_cfg, key='world')

    def deploy(self):
        self._deploy(self['master'], FilePath.MASTER_WORLD_SETTING_PATH)
        self._deploy(self['caves'], FilePath.CAVES_WORLD_SETTING_PATH)

    def load(self):
        data = self._load(FilePath.MASTER_WORLD_SETTING_PATH)
        self['master'] = data
        data = self._load(FilePath.CAVES_WORLD_SETTING_PATH)
        self['caves'] = data

    def _get_init_data(self):
        return {
            'master': {},
            'caves': {}
        }

    def get_master(self) -> dict:
        return self['master']

    def update_master(self, data) -> None:
        self['master'].update(data)

    def get_caves(self) -> dict:
        return self['caves']

    def update_caves(self, data) -> None:
        self['caves'].update(data)

    @staticmethod
    def _deploy(data: dict, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        for key, value in data.items():
            content = re.sub(r'"%s"=".*?"' % key, f'"{key}"="{value}"', content)
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


class ModCfgHandler(BaseCfgHandler):
    def __init__(self, base_cfg: BaseCfg):
        super().__init__(base_cfg, key='mod')

    def deploy(self):
        mod_setting = 'return {\n'
        for mod in self.values():
            mod_enable = mod['enable']
            mod_config = mod['config']
            if not mod_enable:
                continue
            mod_setting += f'  {mod_config},\n'
        mod_setting = mod_setting[-2] + '}\n'
        with open(FilePath.MASTER_MOD_SETTING_PATH, 'w', encoding='utf-8') as f:
            f.write(mod_setting)
        with open(FilePath.CAVES_MOD_SETTING_PATH, 'w', encoding='utf-8') as f:
            f.write(mod_setting)

        mod_setup = ''
        for mod_id in self:
            mod_setup += f'ServerModSetup("{mod_id}")\n'
        with open(FilePath.MOD_SETUP_PATH, 'w', encoding='utf-8') as f:
            f.write(mod_setup)

    def load(self):
        with open(FilePath.MASTER_MOD_SETTING_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        for _, mod in self:
            mod['enable'] = False
        self.add_by_content(content)

    def get_mod_ids(self) -> List[str]:
        return list(self)

    def get_mods(self) -> List[dict]:
        return list(self.values())

    def get_mod(self, mod_id: str) -> Union[None, dict]:
        if mod_id not in self:
            return None
        return self[mod_id]

    def _get_init_data(self):
        return {}

    def update_mod(self, mod_id: str, mod_data: dict) -> int:
        if mod_id not in self:
            return Constants.RET_FAILED
        self[mod_id].update(mod_data)
        return Constants.RET_SUCCEED

    def _add_mod(self, mod_id: str, mod_config: str):
        self[mod_id] = {
            'id': mod_id,
            'name': '',
            'remark': '',
            'version': '',
            'config': mod_config,
            'enable': True
        }

    def add_by_mod_id(self, mod_id: str) -> None:
        mod_config = '["workshop-%s"]={ configuration_options={ }, enabled=true }' % mod_id
        self._add_mod(mod_id, mod_config)

    def add_by_content(self, content: str) -> int:
        mod_ids = re.findall(r'\["workshop-(\d+)"\]=\{.*?\{.*?\}.*?enabled.*?\}', content, re.S)
        mod_configs = re.findall(r'\["workshop-\d+"\]=\{.*?\{.*?\}.*?enabled.*?\}', content, re.S)
        if len(mod_ids) != len(mod_configs):
            log.error(f'regex mod failed: mod_ids={mod_ids}, mod_configs={mod_configs}, content={content}')
            return Constants.RET_FAILED

        for mod_id, mod_config in zip(mod_ids, mod_configs):
            self._add_mod(mod_id, mod_config)
        return Constants.RET_SUCCEED

    def delete(self, mod_ids: List[str]) -> None:
        for mod_id in mod_ids:
            self.pop(mod_id, None)


class Cfg:
    def __init__(self):
        base_cfg = BaseCfg()
        self._base_cfg = base_cfg
        self.common = CommonCfgHandler(base_cfg)
        self.cluster = ClusterCfgHandler(base_cfg)
        self.room = RoomCfgHandler(base_cfg)
        self.world = WorldCfgHandler(base_cfg)
        self.mod = ModCfgHandler(base_cfg)

    def deploy(self):
        self.common.deploy()
        self.cluster.deploy()
        self.room.deploy()
        self.world.deploy()
        self.mod.deploy()

    def load(self):
        self.common.load()
        self.cluster.load()
        self.room.load()
        self.world.load()
        self.mod.load()

    def save(self):
        self._base_cfg.save_cfg()

    def read(self):
        self._base_cfg.read_cfg()


