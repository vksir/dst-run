#!/usr/bin/python3

import os
import re
import json
import subprocess
import threading
from typing import List
from time import strftime, localtime, sleep

import log
import server
import constants
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

    def _room_setting(self):
        # todo
        pass

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
        value = get_choice('Which value to choose?', {
            setting: {i: i for i in WORLD_SETTING_DICT[setting]}
        })
        self._cfg[shard][setting] = value
        self._save_params()

        config.save_world_setting(self._cfg)

    def _show_mod(self):
        mod_dict = config.read_modoverrides(cluster=self._cluster)
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
            mod_dict = config.read_modoverrides(content=content)
            if mod_dict == EXIT_FAILED:
                print('Input format is incorrect.')
                return
        else:
            new_mod_dict = {}
            for mod_id in first_line.split():
                new_mod_dict.update({
                    mod_id: '["workshop-%s"]={ configuration_options={ }, enabled=true }' % mod_id
                })
            mod_dict = config.read_modoverrides(self._cluster)
            mod_dict.update(new_mod_dict)

        config.save_modoverrides(self._cluster, mod_dict)

    def _delete_mod(self):
        mod_id_str = input('Input mod id:')
        mod_dict = config.read_modoverrides(self._cluster)
        for mod_id in mod_id_str.split():
            mod_dict.pop(mod_id, None)
        config.save_modoverrides(self._cluster, mod_dict)

    def _edit_modoverrides_file(self, editor: str):
        modoverrides_path = f'{CLUSTERS_HOME}/{self._cluster}/Master/modoverrides.lua'
        run_cmd(f'{editor} {modoverrides_path}')

    def _mod_setting(self):
        while True:
            executor = get_choice('What to do?', {
                'Mods Show': {
                    'Show Mods List': Executor(self._show_mod)
                },
                'Mods Edit': {
                    'Add Mods': Executor(self._add_mod),
                    'Delete Mods': Executor(self._delete_mod)
                },
                'Edit Modoverrides File': {
                    'By vim': Executor(self._edit_modoverrides_file, editor='vim'),
                    'By nano': Executor(self._edit_modoverrides_file, editor='nano')
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
                    'Cluster Management': Executor(self._cluster_management)
                }
            })
            if executor in [CHOICE_DEFAULT, CHOICE_EXIT]:
                return
            executor.run()

    def _show_info(self):
        # todo
        # run_cmd('clear')
        print(
            f'==================== DST_Run ====================\n'
            f'Room Name:\t\t\t\t{self._cfg[ROOM_NAME_KEY]}\n'
            f'Password:\t\t\t\t{self._cfg[ROOM_PASSWORD_KEY]}\n'
            f'Directly connection:\tc_connect("{self._cfg[IP_KEY]}", 10999)\n'
            f'\n'
            f'Cluster Name:\t\t\t{self._cfg[CLUSTER_KEY]}\n'
            f'Controller Version:\t\t\t{self._cfg[VERSION_KEY]}\n'
            f'============= By Villkiss (Ver 1.1.0)=============\n'
        )

    def _read_params(self):
        self._cfg = config.read_cfg()
        self._cluster = config.get_cluster(self._cfg)

    def _save_params(self):
        config.save_cfg(self._cfg)


if __name__ == '__main__':
    constants.init()
    log.init(stdout=True)
    dst_server = Controller()
    dst_server.run()
