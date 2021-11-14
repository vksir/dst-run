#!/usr/bin/python3
# coding: utf-8

import argparse
import json
from importlib import import_module
from inspect import signature
from typing import List

import requests
from tools import run_cmd
from constants import *
from http_server import Controller


class ArgParserHandler:
    def __init__(self):
        self._enable_debug = False

    def run(self):
        parser = self.get_parser()
        args = parser.parse_args()

        kwargs = dict(args.__dict__)
        method = kwargs.pop('method')
        res = self._control(method, kwargs)

        new_res = {key: value for key, value in res.items() if value is not None}
        print(json.dumps(new_res, indent=4))

    def _control(self, method: str, kwargs: dict = None) -> dict:
        url = f'http://{IP}:{PORT}'
        data = {
            'method': method.replace('-', '_'),
            'kwargs': kwargs or {}
        }

        try:
            resp = requests.post(url, data=json.dumps(data))
            if resp.status_code != 200:
                return self._response(1, info=f'http error: '
                                              f'status_code={resp.status_code}, resp_text={resp.text}')
        except requests.ConnectionError as e:
            return self._response(1, info=f'post failed: error={e}')

        try:
            resp_data = json.loads(resp.text)
            return resp_data
        except json.JSONDecodeError as e:
            return self._response(1, info=f'json decode failed: '
                                          f'resp_text={resp.text}, error={e}')

    @staticmethod
    def get_parser() -> argparse.ArgumentParser:
        def find_parser(objs: List[object]):
            for obj in objs:
                for method_name, method in obj.__dict__.items():
                    if not method_name.startswith('do_'):
                        continue
                    method_name = method_name[3:].replace('_', '-')

                    sub_parser = sub_parsers.add_parser(method_name)
                    sub_parser.set_defaults(method=method_name)
                    parameters = signature(method).parameters
                    for arg_name, arg_parameter in parameters.items():
                        if arg_name == 'self':
                            continue
                        arg_name = arg_name.replace('_', '-')
                        if arg_parameter.default is arg_parameter.empty:
                            sub_parser.add_argument(f'--{arg_name}', required=True)
                        else:
                            sub_parser.add_argument(f'--{arg_name}', required=False, default=arg_parameter.default)

        parser = argparse.ArgumentParser(description='dst-run cli')
        sub_parsers = parser.add_subparsers(title='methods')
        find_parser([import_module('cli'), Controller])
        return parser

    @staticmethod
    def _response(ret: int,
                  info: str = None,
                  player_list: list = None,
                  mod_list: list = None) -> dict:
        return locals()

    def _print(self, *args, **kwargs):
        if self._enable_debug:
            print(*args, **kwargs)


def do_install():
    cmd_lst = ['apt install libstdc++6:i386 libgcc1:i386 libcurl4-gnutls-dev:i386 -y',
               'mkdir -p %s' % STEAMCMD_HOME,
               'wget "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz"',
               'tar -xzvf steamcmd_linux.tar.gz',
               'rm steamcmd_linux.tar.gz']
    for cmd in cmd_lst:
        run_cmd(cmd, cwd=STEAMCMD_HOME, sudo=True)
    Controller.server_update()


def do_set_log_level(level):
    pass


if __name__ == '__main__':
    ap = ArgParserHandler()
    ap.run()
