import io
import json
import re
import time
from typing import List, IO
from copy import deepcopy
from contextlib import contextmanager, ContextDecorator
from configparser import ConfigParser, SectionProxy

import constants
from log import log
from constants import *
from tools import run_cmd, get_choice


class CfgParser:
    def __init__(self):
        if not os.path.exists(CFG_PATH):
            self._init_cfg()

    @staticmethod
    def read() -> dict:
        with open(CFG_PATH, 'r') as f:
            return json.load(f)

    @staticmethod
    def write(cfg: dict):
        with open(CFG_PATH, 'w') as f:
            json.dump(cfg, f, indent=4)

    def _init_cfg(self):
        version = get_version()
        cfg = {
            CLUSTER_KEY: 'Cluster_1',
            ENABLE_REFORGED_KEY: False,
            ENABLE_CAVES_KEY: True,
            ENABLE_64BIT_KEY: True,
            CLUSTER_TOKEN_KEY: '',
            VERSION_KEY: version,
            EDITOR_KEY: VIM,
            TEMPLATE_KEY: DEFAULT,
            WHITE_LIST_KEY: ['127.0.0.1'],

            ROOM_NAME_KEY: 'DST Run',
            ROOM_PASSWORD_KEY: '6666',
            ROOM_DESCRIPTION_KEY: '',
            GAME_MODE_KEY: ENDLESS_MODE,
            MAX_PLAYERS_KEY: '6',
            PVP_KEY: FALSE,
            TICK_RATE_KEY: '30',
            ADMIN_LIST_KEY: [],

            MASTER: {
                WORLD_SIZE_KEY: DEFAULT,
                SPECIAL_EVENT_KEY: DEFAULT
            },
            CAVES: {
                WORLD_SIZE_KEY: DEFAULT,
                SPECIAL_EVENT_KEY: DEFAULT
            }
        }
        self.write(cfg)
        print(f'Please edit the configuration file.\n'
              f'You could run this command:\n'
              f'  vim {CFG_PATH}')
        exit()


def read_modoverrides(cfg: dict, content=None):
    """get mod_dict

    from modoverrides.lua content

    :return: [{MOD_ID_KEY: mod_id, MOD_OPTION_KEY: mod_option}], EXIT_FAILED
    """

    if content:
        data = content
    else:
        cluster = get_cluster(cfg)
        modoverrides_path = f'{CLUSTERS_HOME}/{cluster}/Master/modoverrides.lua'
        if not os.path.exists(modoverrides_path):
            log.info(f"path doesn't exit: {modoverrides_path}")
            return {}
        with open(modoverrides_path, 'r') as f:
            data = f.read()

    mod_dict = {}
    try:
        id_lst = re.findall(r'(?<="workshop-).*?(?=")', data)
        option_lst = re.findall(r'\[.*?enabled.*?\}', data, re.S)
        for i in range(len(id_lst)):
            mod_dict.update({id_lst[i]: option_lst[i]})
        return mod_dict
    except Exception as e:
        log.error(f'regular modoverrides failed: data={data}, error={e}')
        return EXIT_FAILED


def save_modoverrides(cfg: dict, mod_dict: dict):
    cluster = get_cluster(cfg)
    modoverrides_path = _get_modoverrides_path(cluster)
    with open(modoverrides_path, 'w') as f:
        f.write('return {\n')
        mod_lst = list(mod_dict.values())
        if mod_lst:
            for mod in mod_lst:
                f.write(f'  {mod}{"," if mod is mod_lst[-1] else ""}\n')
        f.write('}\n')


def edit_modoverrides(cfg: dict):
    cluster = get_cluster(cfg)
    _edit_file(cfg.get(EDITOR_KEY), path=_get_modoverrides_path(cluster))


def save_mod_setup(cfg: dict):
    cluster = get_cluster(cfg)

    master_modoverrides_path = f'{CLUSTERS_HOME}/{cluster}/Master/modoverrides.lua'
    caves_modoverrides_path = f'{CLUSTERS_HOME}/{cluster}/Caves/modoverrides.lua'
    mod_setup_path = f'{DST_HOME}/mods/dedicated_server_mods_setup.lua'

    with open(mod_setup_path, 'w') as f:
        mod_dict = read_modoverrides(cfg)
        for mod_id in mod_dict:
            f.write(f'ServerModSetup("{mod_id}")\n')

    if cfg[ENABLE_CAVES_KEY]:
        run_cmd(f'cp -f {master_modoverrides_path} {caves_modoverrides_path}')


def create_cluster(cfg: dict):
    cluster = get_cluster(cfg)
    cluster_path = f'{CLUSTERS_HOME}/{cluster}'
    if os.path.exists(cluster_path):
        run_cmd(f'rm -rf {cluster_path}')

    template = cfg.get(TEMPLATE_KEY)
    template_path = f'{TEMPLATE_HOME}/{template}'
    run_cmd(f'cp -rf {template_path} {cluster_path}')
    return


def backup_cluster(cfg: dict):
    cluster = get_cluster(cfg)
    file_name = time.strftime(f'{cluster}_%Y-%m-%d_%H-%M-%S', time.localtime())
    run_cmd(f'tar -czvf {CLUSTERS_BACKUP_HOME}/{file_name}.tar.gz {cluster}', cwd=CLUSTERS_HOME)


def save_world_setting(cfg: dict):
    cluster = get_cluster(cfg)
    for shard in [MASTER, CAVES]:
        shard_world_setting_path = f'{CLUSTERS_HOME}/{cluster}/{shard}/leveldataoverride.lua'
        with open(shard_world_setting_path, 'r') as f:
            data = f.read()
        for option, value in cfg.get(shard).items():
            data = re.sub(r'(?<=%s=").*?(?=")' % option, value, data)
        with open(shard_world_setting_path, 'w') as f:
            f.write(data)


def _get_section(parser: ConfigParser, section: str) -> SectionProxy:
    if not parser.has_section(section):
        parser.add_section(section)
    return parser[section]


def save_room_setting(cfg: dict):
    cluster = get_cluster(cfg)
    room_setting_path = f'{CLUSTERS_HOME}/{cluster}/cluster.ini'
    cluster_parser = ConfigParser()
    cluster_parser.read(room_setting_path)

    if cluster != REFORGED:
        section_proxy = _get_section(cluster_parser, 'GAMEPLAY')
        section_proxy['game_mode'] = cfg.get(GAME_MODE_KEY)
        section_proxy['max_players'] = cfg.get(MAX_PLAYERS_KEY)
        section_proxy['pvp'] = cfg.get(PVP_KEY)

    section_proxy = _get_section(cluster_parser, 'NETWORK')
    section_proxy['cluster_name'] = '{0}{1}{0}'.format(NAME_SURROUND, cfg.get(ROOM_NAME_KEY))
    section_proxy['cluster_password'] = cfg.get(ROOM_PASSWORD_KEY)
    section_proxy['cluster_description'] = cfg.get(ROOM_DESCRIPTION_KEY)
    section_proxy['tick_rate'] = cfg.get(TICK_RATE_KEY)

    with open(room_setting_path, 'w') as f:
        cluster_parser.write(f)


def save_token(cfg: dict):
    cluster = get_cluster(cfg)
    with open(f'{CLUSTERS_HOME}/{cluster}/cluster_token.txt', 'w') as f:
        f.write(cfg[CLUSTER_TOKEN_KEY])


def read_admin_lst(cfg: dict) -> List[str]:
    cluster = get_cluster(cfg)
    admin_list_path = _get_admin_lst_path(cluster)
    if not os.path.exists(admin_list_path):
        return []

    admin_lst = []
    with open(admin_list_path, 'r') as f:
        for admin in f:
            admin_lst.append(admin)
    return admin_lst


def save_admin_lst(cfg: dict):
    cluster = get_cluster(cfg)
    admin_lst_path = _get_admin_lst_path(cluster)
    with open(admin_lst_path, 'w') as f:
        for admin in cfg.get(ADMIN_LIST_KEY):
            f.write(f'{admin}\n')


def edit_admin_lst(cfg: dict):
    cluster = get_cluster(cfg)
    _edit_file(cfg.get(EDITOR_KEY), path=_get_admin_lst_path(cluster))


def get_version() -> str:
    try:
        with open(f'{DST_HOME}/version.txt', 'r') as f:
            version = f.read().strip()
            return version
    except Exception as e:
        log.error(f'get version failed: {e}')
        return ''


def get_ip():
    # todo
    return ''


def _edit_file(editor: str, path: str):
    run_cmd(f'{editor} {path}')


def get_cluster(cfg: dict) -> str:
    return REFORGED if cfg[ENABLE_REFORGED_KEY] else cfg[CLUSTER_KEY]


def get_cluster_path(cluster: str) -> str:
    return f'{CLUSTERS_HOME}/{cluster}'


def _get_modoverrides_path(cluster: str, shard=MASTER) -> str:
    return f'{CLUSTERS_HOME}/{cluster}/{shard}/modoverrides.lua'


def _get_world_setting_path(cluster: str, shard=MASTER) -> str:
    return f'{CLUSTERS_HOME}/{cluster}/{shard}/leveldataoverride.lua'


def _get_cluster_ini_path(cluster: str) -> str:
    return f'{CLUSTERS_HOME}/{cluster}/cluster.ini'


def _get_admin_lst_path(cluster: str) -> str:
    return f'{CLUSTERS_HOME}/{cluster}/adminlist.txt'


def init_path():
    path_lst = dir(constants)
    for path in path_lst:
        if path.endswith('HOME') and not os.path.exists(eval(path)):
            run_cmd(f'mkdir -p {eval(path)}')


class ServerLogWriter:
    def __init__(self):
        self._fd = None

    def init_fd(self) -> IO:
        self._fd = open(GAME_LOG_PATH, 'w')
        return self._fd

    def close_fd(self):
        if self._fd:
            self._fd.close()

    def get_fd(self) -> IO:
        return self._fd


class ServerLogReader(ContextDecorator):
    def __enter__(self):
        self._fd = open(GAME_LOG_PATH, 'rb')
        self._fd.seek(0, io.SEEK_END)
        return self

    def __exit__(self, *args):
        self._fd.close()

    def read(self):
        # todo
        return self._fd.read().decode(errors='replace').encode(errors='replace').decode(errors='replace').replace('?', '')
