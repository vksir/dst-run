#!/usr/bin/python3

import signal
from typing import List

import log
import config
from tools import run_cmd, get_choice, Executor
from constants import *
from server import Server


class Controller:
    _cfg: dict = None
    _cluster: str = None

    def __init__(self):
        self._read_params()
        self._server = Server()

    def _start_server(self, update=False):
        if not os.path.exists(f'{CLUSTERS_HOME}/{self._cluster}'):
            config.create_cluster(self._cfg)
        if update:
            self._server.server_update()
        self._server.run()

    def _new_cluster(self):
        if self._cluster == REFORGED:
            self._cfg[ENABLE_REFORGED_KEY] = False
            self._save_params()

        is_create = get_choice('Are you sure to generate a new cluster?', expect_choice=False)
        if is_create == CHOICE_NO:
            return

        is_backup = get_choice('Backup current cluster?', expect_choice=True)
        if is_backup == CHOICE_YES:
            config.backup_cluster(self._cluster)
        config.create_cluster(self._cfg)

    def _set_cfg_by_input(self, cfg_key: str, title: str, only_digit=False):
        value = input(title)
        if only_digit:
            while not value.isdigit():
                value = input(f'{title}:(only digit) ')
        self._cfg.update({cfg_key: value})
        self._save_params()

    def _set_cfg_by_choice(self, cfg_key: str, title: str, choice_lst: List[str]):
        value = get_choice('Which to choose?', {
            title: {i: i for i in choice_lst}
        })
        if value in [CHOICE_DEFAULT, CHOICE_EXIT]:
            return

        self._cfg.update({cfg_key: value})
        self._save_params()

    def _set_admin_lst(self):
        config.edit_admin_lst(self._cfg)
        admin_lst = config.read_admin_lst(self._cfg)
        self._cfg.update({ADMIN_LIST_KEY: admin_lst})
        self._save_params()

        config.save_admin_lst(self._cfg)

    def _room_setting(self):
        executor = get_choice('Which to change?', {
            'Room Setting': {
                'Room Name': Executor(self._set_cfg_by_input, ROOM_NAME_KEY, 'Room Name: '),
                'Room Password': Executor(self._set_cfg_by_input, ROOM_PASSWORD_KEY, 'Room Password: ', True),
                'Room Description': Executor(self._set_cfg_by_input, ROOM_DESCRIPTION_KEY, 'Room Description: '),
                'Game Mode': Executor(self._set_cfg_by_choice, GAME_MODE_KEY, 'Game Mode', GAME_MOD_LIST),
                'Max Players': Executor(self._set_cfg_by_input, MAX_PLAYERS_KEY, 'Max Players: ', True),
                'PVP': Executor(self._set_cfg_by_choice, PVP_KEY, 'Enable PVP', TRUE_FALSE_LIST),
                'Tick Rate': Executor(self._set_cfg_by_input, TICK_RATE_KEY, 'Tick Rate: ', True),
                'Admin List': Executor(self._set_admin_lst())
            }
        })
        if executor in [CHOICE_DEFAULT, CHOICE_EXIT]:
            return
        executor.run()

    def _world_setting(self):
        if self._cfg[ENABLE_REFORGED_KEY]:
            print("Reforged world doesn't need to set.")
            return

        shard = get_choice('Which shard to change?', {
            'Shard': {
                'Master Setting': MASTER,
                'Caves Setting': CAVES
            }
        })
        if shard in [CHOICE_DEFAULT, CHOICE_EXIT]:
            return

        setting = get_choice('Which setting to change?', {
            f'{shard} Setting': {i: i for i in self._cfg[shard]}
        })
        if setting in [CHOICE_DEFAULT, CHOICE_EXIT]:
            return

        value = get_choice('Which value to choose?', {
            setting: {i: i for i in WORLD_SETTING_DICT[setting]}
        })
        if value in [CHOICE_DEFAULT, CHOICE_EXIT]:
            return

        self._cfg[shard][setting] = value
        self._save_params()

        config.save_world_setting(self._cfg)

    def _show_mod(self):
        mod_dict = config.read_modoverrides(self._cfg)
        print('Mod List:')
        for i, mod_id in enumerate(mod_dict.keys()):
            print(f'  ({i + 1}) {mod_id}')

    def _add_mod(self):
        print('Input one of following\n'
              '  1) all content in modoverrides file\n'
              '  2) mod id\n'
              'to add mod:')
        first_line = input()
        if 'return' in first_line:
            content, read_ = first_line, ''
            while read_ != '}':
                read = input()
                content += read
            mod_dict = config.read_modoverrides(self._cfg, content=content)
            if mod_dict == EXIT_FAILED:
                print('Input format is incorrect.')
                return
        else:
            new_mod_dict = {}
            for mod_id in first_line.split():
                new_mod_dict.update({
                    mod_id: '["workshop-%s"]={ configuration_options={ }, enabled=true }' % mod_id
                })
            mod_dict = config.read_modoverrides(self._cfg)
            mod_dict.update(new_mod_dict)

        config.save_modoverrides(self._cfg, mod_dict)

    def _delete_mod(self):
        mod_id_str = input('Input mod id:')
        mod_dict = config.read_modoverrides(self._cfg)
        for mod_id in mod_id_str.split():
            mod_dict.pop(mod_id, None)
        config.save_modoverrides(self._cfg, mod_dict)

    def _mod_setting(self):
        while True:
            executor = get_choice('What to do?', {
                'Mods Show': {
                    'Show Mods List': Executor(self._show_mod)
                },
                'Mods Edit': {
                    'Add Mods': Executor(self._add_mod),
                    'Delete Mods': Executor(self._delete_mod),
                    'Edit Modoverrides File': Executor(config.edit_modoverrides)
                }
            })
            if executor in [CHOICE_DEFAULT, CHOICE_EXIT]:
                return
            executor.run()

    def _cluster_management(self):
        self._show_info()
        cluster_lst = [f'Cluster_{i}' for i in range(1, 4)]
        choice = get_choice('What to do?', {
            'Change Controller Type': {
                'Master & Caves': [ENABLE_CAVES_KEY],
                'Only Master': [],
                'Reforged': [ENABLE_REFORGED_KEY]
            },
            'Change Cluster': {i: i for i in cluster_lst}
        })
        if choice in [CHOICE_DEFAULT, CHOICE_EXIT]:
            return

        if choice not in cluster_lst:
            enable_lst = [ENABLE_CAVES_KEY, ENABLE_REFORGED_KEY]
            for key in choice:
                self._cfg.update({key: key in enable_lst})
        self._save_params()

    def _other_setting(self):
        executor = get_choice('Which to change?', {
            'Setting': {
                'Enable 64-bit': Executor(self._set_cfg_by_choice, ENABLE_64BIT_KEY, 'Enable 64-bit', TRUE_FALSE_LIST),
                'Editor': Executor(self._set_cfg_by_choice, EDITOR_KEY, 'Editor', EDITOR_LIST)
            }
        })
        if executor in [CHOICE_DEFAULT, CHOICE_EXIT]:
            return
        executor.run()

    def run(self):
        while True:
            self._show_info()
            executor = get_choice('What to do?', {
                'Start': {
                    'Run': Executor(self._start_server),
                    'Update/Run': Executor(self._start_server, update=True),
                    'New Cluster': Executor(self._new_cluster)
                },
                'Setting': {
                    'Room Setting': Executor(self._room_setting),
                    'World Setting': Executor(self._world_setting),
                    'Mods Setting': Executor(self._mod_setting)
                },
                OTHERS_KEY: {
                    'Cluster Management': Executor(self._cluster_management),
                    'Other Setting': Executor(self._other_setting)
                }
            })
            if executor in [CHOICE_DEFAULT, CHOICE_EXIT]:
                return
            executor.run()

    def _show_info(self):
        run_cmd('clear')
        print(
            f'==================== DST_Run ====================\n'
            f'Room Name:\t\t\t\t{self._cfg[ROOM_NAME_KEY]}\n'
            f'Password:\t\t\t\t{self._cfg[ROOM_PASSWORD_KEY]}\n'
            f'Directly connection:\tc_connect("{self._cfg[IP_KEY]}", 10999)\n'
            f'\n'
            f'Cluster Name:\t\t\t{self._cfg[CLUSTER_KEY]}\n'
            f'Version:\t\t\t{self._cfg[VERSION_KEY]}\n'
            f'============= By Villkiss (Ver 1.1.0)=============\n'
        )

    def _read_params(self):
        self._cfg = config.read_cfg()
        self._cluster = config.get_cluster(self._cfg)

    def _save_params(self):
        config.save_cfg(self._cfg)


def main():
    def safe_exit(*args):
        exit()
    signal.signal(signal.SIGINT, safe_exit)

    config.init_path()
    log.init(stdout=True)
    dst_server = Controller()
    dst_server.run()


if __name__ == '__main__':
    main()
