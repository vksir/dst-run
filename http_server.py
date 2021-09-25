import json
from typing import List
from wsgiref.simple_server import make_server

from webob import Request, Response

import config
from log import log
from tools import run_cmd, get_choice, Executor
from constants import *
from controller import Controller, response


class Application:
    _cfg: dict = None
    _cluster: str = None

    def __init__(self):
        self._read_params()
        self._controller = Controller()

    def __call__(self, env, start_response):
        req = Request(env)
        resp = Response()
        remote_addr = req.remote_addr
        body = req.body
        if remote_addr not in WHITE_LST:
            resp.status_code = 401
            return resp(env, start_response)

        try:
            data = json.loads(body.decode())
        except Exception as e:
            info = 'json loads body failed'
            log.error(f'{info}: body={body}, remote_addr={remote_addr}, error={e}')
            resp.body = json.dumps(response(1, info=info)).encode()
            return resp(env, start_response)

        resp_data = self._deal_with_data(remote_addr, data)
        resp.body = json.dumps(resp_data).encode()
        return resp(env, start_response)

    def _deal_with_data(self, remote_addr: str, data: dict) -> dict:
        log.info(f'receive request: data={data}')
        method = data.get('method')

        if not method:
            info = 'get method failed'
            log.error(f'{info}: data={data}, remote_addr={remote_addr}')
            return response(1, info=info)

        method = 'do_' + method
        if not hasattr(self._controller, method):
            info = 'method not found'
            log.error(f'{info}: method={method}, data={data}, remote_addr={remote_addr}')
            return response(1, info=info)

        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        try:
            res = getattr(self._controller, method)(*args, **kwargs)
            return res
        except Exception as e:
            info = 'run method failed'
            log.error(f'{info}: method={method}, data={data}, remote_addr={remote_addr}, error={e}')
            return response(1, info=info)

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
        executor.start()

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
            executor.start()

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
        executor.start()

    def _read_params(self):
        self._cfg = config.read_cfg()
        self._cluster = config.get_cluster(self._cfg)

    def _save_params(self):
        config.save_cfg(self._cfg)


class HttpServer:
    def __init__(self, app, port=5800):
        self._app = app
        self._port = port

    def start(self):
        with make_server('', self._port, self._app) as httpd:
            print('http server start')
            httpd.serve_forever()

    @staticmethod
    def stop():
        file_name = os.path.split(__file__)[-1]
        log.debug(f'stop http server: file_name={file_name}')
        run_cmd("ps -ef | grep -v grep | grep %s | awk '{print $2}' | xargs kill -9" % file_name, shell=True)
