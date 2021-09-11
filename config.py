
import json
import re
import time
from typing import List

import log
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

        ROOM_NAME_KEY: 'DST Run',
        ROOM_PASSWORD_KEY: '6666',
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


def read_modoverrides(content=None, cluster=None):
    """get mod_dict

    from modoverrides.lua content

    :return: [{MOD_ID_KEY: mod_id, MOD_OPTION_KEY: mod_option}], EXIT_FAILED
    """

    if content:
        data = content
    elif cluster:
        modoverrides_path = f'{CLUSTERS_HOME}/{cluster}/Master/modoverrides.lua'
        if not os.path.exists(modoverrides_path):
            log.info(f"path doesn't exit: {modoverrides_path}")
            return {}
        with open(modoverrides_path, 'r') as f:
            data = f.read()
    else:
        raise Exception('read_modoverrides() need modoverrides_content or cluster, but none of them got')

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


def save_modoverrides(cluster: str, mod_dict: dict):
    with open(f'{CLUSTERS_HOME}/{cluster}/Master/modoverrides.lua', 'w') as f:
        f.write('return {\n')
        mod_lst = list(mod_dict.values())
        if mod_lst:
            for mod in mod_lst:
                f.write(f'  {mod}{"," if mod is mod_lst[-1] else ""}\n')
        f.write('}\n')


def set_mod_setup(cfg: dict):
    cluster = get_cluster(cfg)

    master_modoverrides_path = f'{CLUSTERS_HOME}/{cluster}/Master/modoverrides.lua'
    caves_modoverrides_path = f'{CLUSTERS_HOME}/{cluster}/Caves/modoverrides.lua'
    mod_setup_path = f'{DST_HOME}/mods/dedicated_server_mods_setup.lua'

    with open(mod_setup_path, 'w') as f:
        mod_dict = read_modoverrides(cluster=cluster)
        for mod_id in mod_dict:
            f.write(f'ServerModSetup("{mod_id}")\n')

    if cfg[ENABLE_CAVES_KEY]:
        run_cmd(f'cp -f {master_modoverrides_path} {caves_modoverrides_path}')


def create_cluster(cluster: str):
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

    run_cmd(f'cp -rf {USER_TEMPLATE_HOME}/{template} {cluster_path}')


def backup_cluster(cluster: str):
    if os.path.exists(f'{CLUSTERS_HOME}/{cluster}'):
        file_name = time.strftime(f'{cluster}_%Y-%m-%d_%H-%M-%S', time.localtime())
        run_cmd(f'tar -czvf {CLUSTERS_BACKUP_HOME}/{file_name}.tar.gz {cluster}', cwd=CLUSTERS_HOME)


def set_token(cfg: dict):
    cluster = get_cluster(cfg)
    with open(f'{CLUSTERS_HOME}/{cluster}/cluster_token.txt', 'w') as f:
        f.write(cfg[CLUSTER_TOKEN_KEY])


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


def get_cluster(cfg: dict) -> str:
    return REFORGED if cfg[ENABLE_REFORGED_KEY] else cfg[CLUSTER_KEY]
