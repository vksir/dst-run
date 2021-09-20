import json
import re
import time
from typing import List
from copy import deepcopy
from contextlib import contextmanager
from configparser import ConfigParser, SectionProxy

import log
import constants
from constants import *
from tools import run_cmd, get_choice


def _init_cfg() -> dict:
    cluster_token = input('No cluster_token found.\n'
                          'Please input your cluster_token: ')
    ip = get_ip()
    version = get_version()
    cfg = {
        CLUSTER_KEY: 'Cluster_1',
        ENABLE_REFORGED_KEY: False,
        ENABLE_CAVES_KEY: True,
        ENABLE_64BIT_KEY: True,
        CLUSTER_TOKEN_KEY: cluster_token,
        IP_KEY: ip,
        VERSION_KEY: version,
        EDITOR_KEY: VIM,

        ROOM_NAME_KEY: 'DST Run',
        ROOM_PASSWORD_KEY: '6666',
        ROOM_DESCRIPTION_KEY: '',
        GAME_MODE_KEY: ENDLESS_MODE,
        MAX_PLAYERS_KEY: '6',
        PVP_KEY: FALSE,
        TICK_RATE_KEY: '15',
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
    save_cfg(cfg)
    return cfg


def read_cfg() -> dict:
    try:
        with open(CFG_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        log.error(f'read cfg: {e}')
        return _init_cfg()


def save_cfg(cfg: dict):
    with open(CFG_PATH, 'w') as f:
        json.dump(cfg, f)


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

    if cluster == REFORGED:
        template_path = f'{TEMPLATE_HOME}/{REFORGED}'
        run_cmd(f'cp -rf {template_path} {cluster_path}')
        return

    template_lst = os.listdir(TEMPLATE_HOME)
    template_lst.remove(DEFAULT)
    template_lst.insert(0, DEFAULT)
    user_template_lst = os.listdir(USER_TEMPLATE_HOME)
    log.debug(f'template_lst={template_lst}, user_template_lst={user_template_lst}')

    template = get_choice('Cluster Template:', {
        'Default': {i: i for i in template_lst},
        'User': {i: i for i in user_template_lst}
    })
    if template in [CHOICE_EXIT, CHOICE_DEFAULT]:
        template = DEFAULT

    if template in template_lst:
        cmd = f'cp -rf {TEMPLATE_HOME}/{template} {cluster_path}'
    else:
        cmd = f'cp -rf {USER_TEMPLATE_HOME}/{template} {cluster_path}'
    run_cmd(cmd)

    save_room_setting(cfg)
    save_world_setting(cfg)


def backup_cluster(cluster: str):
    if os.path.exists(f'{CLUSTERS_HOME}/{cluster}'):
        name = input('Input backup filename: (Empty to use default name) ')
        file_name = time.strftime(f'{name if name else cluster}_%Y-%m-%d_%H-%M-%S', time.localtime())
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
        if (path.endswith('PATH') or path.endswith('HOME')) \
                and not os.path.exists(eval(path)):
            run_cmd(f'mkdir -p {eval(path)}')
