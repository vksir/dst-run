#!/usr/bin/python3
# coding: utf-8

import argparse
import json
from pprint import pprint

import requests
from log import log
from tools import run_cmd
from constants import *
from http_server import Controller


parser = argparse.ArgumentParser(description='dst-run cli')
parser.add_argument('-a', '--action', dest='action', type=str,
                    help='dst-run action')
parser.add_argument('-c', '--control', dest='method', type=str,
                    help='dst-server control')
parser.add_argument('-args', dest='args', type=str, metavar='arg1,arg2',
                    help='function args')
parser.add_argument('-kwargs', dest='kwargs', type=str, metavar='key1=value1,key2=value2',
                    help='function kwargs')


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


def remote_run(method: str, args: list = None, kwargs: dict = None, ip='127.0.0.1', port=5800):
    url = f'http://{ip}:{port}'
    data = {'method': method}
    if args:
        data['args'] = args
    if kwargs:
        data['kwargs'] = kwargs

    try:
        res = requests.post(url, data=json.dumps(data))
    except requests.ConnectionError:
        return 'connect refused'

    try:
        recv_data = json.loads(res.text)
    except json.JSONDecodeError:
        recv_data = res.text
    return recv_data


def main():
    args = parser.parse_args()
    if args.action:
        action = 'do_' + args.action
        # todo
        return

    if args.method:
        method = args.method
        res = remote_run(method)
        pprint(res, sort_dicts=False)


if __name__ == '__main__':
    main()