import re
import time
import abc
from typing import Dict, Any, List
from configparser import ConfigParser
import yaml
from dst_run.common.log import log
from dst_run.common.constants import *
from dst_run.common.utils import run_cmd
from dst_run.routes.models import *
from dst_run.routes.world_setting_models import Master, Caves


class BaseCfg(abc.ABC, BaseModel):
    @abc.abstractmethod
    def deploy(self):
        pass

    @abc.abstractmethod
    def read(self):
        pass


class ProgramCfg(BaseCfg):
    ip_whitelist: list = ['127.0.0.1']

    def deploy(self):
        pass

    def read(self):
        pass


class ServerCfg(BaseCfg):
    enable_64bit: bool = True
    enable_caves: bool = True
    version: str = ''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.read_version()

    def deploy(self):
        pass

    def read(self):
        pass

    @staticmethod
    def read_version():
        version_path = f'{DST_DIR}/version.txt'
        if not os.path.exists(version_path):
            return ''
        with open(version_path, 'r', encoding='utf-8') as f:
            return f.read().strip()


class ClusterCfg(BaseCfg):
    used_cluster: str = None
    used_template: str = 'default'
    token: str = ''
    admins: list = []

    def deploy(self):
        self.create(force=False)
        self._deploy_admins()
        self._deploy_token()

    def read(self):
        self.deploy()

    def _deploy_admins(self):
        admin_setting = '\n'.join(self.admins)
        with open(ADMIN_LIST_PATH, 'w', encoding='utf-8') as f:
            f.write(admin_setting)

    def _deploy_token(self):
        with open(CLUSTER_TOKEN_PATH, 'w', encoding='utf-8') as f:
            f.write(self.token)

    @staticmethod
    def backup():
        cluster_path = f'{CLUSTERS_DIR}/{CLUSTER_NAME}'
        if not os.path.exists(cluster_path):
            return
        file_name = time.strftime(f'%Y-%m-%d_%H-%M-%S', time.localtime())
        run_cmd(f'tar -czvf {CLUSTERS_BACKUP_DIR}/{file_name}.tar.gz {CLUSTER_NAME}', cwd=CLUSTERS_DIR)

    def create(self, force=True):
        cluster_path = f'{CLUSTERS_DIR}/{CLUSTER_NAME}'
        if not force and os.path.exists(cluster_path):
            return

        template = self.used_template
        default_template_path = f'{TEMPLATE_DIR}/{template}'
        custom_template_path = f'{CUSTOM_TEMPLATE_DIR}/{template}'
        if os.path.exists(default_template_path):
            template_path = default_template_path
        elif os.path.exists(custom_template_path):
            template_path = custom_template_path
        else:
            log.error(f'template not found: template={template}')
            template_path = f'{TEMPLATE_DIR}/default'

        self.backup()
        run_cmd(f'rm -rf {cluster_path}')
        run_cmd(f'cp -rf {template_path} {cluster_path}')


class RoomCfg(BaseCfg):
    __root__: Dict[str, Dict[str, Any]] = {}

    def deploy(self):
        room_setting = ConfigParser()
        with open(ROOM_SETTING_PATH, 'r', encoding='utf-8') as f:
            room_setting.read_file(f)
        for section_key, section in self.__root__.items():
            for key, value in section.items():
                room_setting[section_key][key] = value
        with open(ROOM_SETTING_PATH, 'w', encoding='utf-8') as f:
            room_setting.write(f)

    def read(self):
        room_setting = ConfigParser()
        with open(ROOM_SETTING_PATH, 'r', encoding='utf-8') as f:
            room_setting.read_file(f)
        data = room_setting._sections
        self.__root__.update(Room(**data).dict())


class WorldCfg(BaseCfg):
    master: Dict[str, str] = {}
    caves: Dict[str, str] = {}

    def deploy(self):
        self._deploy(self.master, MASTER_WORLD_SETTING_PATH)
        self._deploy(self.caves, CAVES_WORLD_SETTING_PATH)

    def read(self):
        data = self._read(MASTER_WORLD_SETTING_PATH)
        self.master = Master(**data).dict()
        data = self._read(CAVES_WORLD_SETTING_PATH)
        self.caves = Caves(**data).dict()

    @staticmethod
    def _deploy(data: dict, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        for key, value in data.items():
            content = re.sub(r'"%s"=".*?"' % key, f'"{key}"="{value}"', content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def _read(file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        data = re.search(r'overrides=\{.*?\}', content, re.S).group()
        data = re.findall(r'([^\s]+?)="([^\s]+?)"', data)
        data = {item[0]: item[1] for item in data}
        return data


class ModCfg(BaseCfg):
    __root__: Dict[str, Mod] = {}

    def deploy(self):
        mod_setting = 'return {\n'
        for mod in self.dict().values():
            if not mod.enable:
                continue
            mod_setting += f'  {mod},\n'
        mod_setting = mod_setting[-2]
        mod_setting += '}\n'
        with open(MASTER_MOD_SETTING_PATH, 'w', encoding='utf-8') as f:
            f.write(mod_setting)
        with open(CAVES_MOD_SETTING_PATH, 'w', encoding='utf-8') as f:
            f.write(mod_setting)

        mod_setup = ''
        for mod_id in self.dict():
            mod_setup += f'ServerModSetup("{mod_id}")\n'
        with open(MOD_SETUP_PATH, 'w', encoding='utf-8') as f:
            f.write(mod_setup)

    def read(self):
        with open(MASTER_MOD_SETTING_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        for _, mod in self.__root__.items():
            mod.enable = False
        self.add_by_content(content)

    def add_by_mod_ids(self, mod_ids: List[str]):
        mods = {}
        for mod_id in mod_ids:
            mod_config = '["workshop-%s"]={ configuration_options={ }, enabled=true }' % mod_id
            mods[mod_id] = Mod(id=mod_id, config=mod_config)
        self.__root__.update(mods)

    def add_by_content(self, data: str):
        mods = {}
        try:
            mod_ids = re.findall(r'\["workshop-(\d+)"\]=\{.*?\{.*?\}.*?enabled.*?\}', data, re.S)
            mod_configs = re.findall(r'\["workshop-\d+"\]=\{.*?\{.*?\}.*?enabled.*?\}', data, re.S)
            if len(mod_ids) != len(mod_configs):
                log.error(f'regex mod failed: mod_ids={mod_ids}, mod_configs={mod_configs}, data={data}')
                return Ret.FAILED
            for mod_id, mod_config in zip(mod_ids, mod_configs):
                mods[mod_id] = Mod(id=mod_id, config=mod_config)
        except Exception as e:
            log.error(f'regex mod failed: data={data}, e={e}')
            return Ret.FAILED
        self.__root__.update(mods)
        return Ret.SUCCESS

    def delete(self, mod_ids: List[str]):
        for mod_id in mod_ids:
            self.__root__.pop(mod_id, None)


class Cfg(BaseCfg):
    program: ProgramCfg = ProgramCfg()
    server: ServerCfg = ServerCfg()
    cluster: ClusterCfg = ClusterCfg()
    room: RoomCfg = RoomCfg()
    world: WorldCfg = WorldCfg()
    mod: ModCfg = ModCfg()

    def __init__(self):
        super().__init__()
        if not os.path.exists(CFG_PATH):
            self.save_cfg()
        self.read_cfg()
        self.read()

    def read(self):
        self.program.read()
        self.server.read()
        self.cluster.read()
        self.room.read()
        self.world.read()
        self.room.read()

        self.save_cfg()

    def deploy(self):
        self.program.deploy()
        self.server.deploy()
        self.cluster.deploy()
        self.room.deploy()
        self.world.deploy()
        self.mod.deploy()

    def read_cfg(self):
        with open(CFG_PATH, 'r', encoding='utf-8') as f:
            cfg = yaml.load(f, Loader=yaml.Loader)
            super().__init__(**cfg)

    def save_cfg(self):
        with open(CFG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(self.dict(), f, sort_keys=False)

