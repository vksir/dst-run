import io
import re
import time
import threading
from functools import wraps
from threading import Thread
from typing import List, IO
from subprocess import Popen

import config
from log import log
from config import ServerLogWriter, ServerLogReader
from constants import *
from tools import run_cmd


INTERVAL = 60


def response(ret: int,
             info: str = None,
             player_list: list = None,
             mod_list: list = None) -> dict:
    return locals()


class Controller:
    def __init__(self, parser: config.CfgParser):
        self._proc_lst: List[Popen] = []
        self._log_writer = ServerLogWriter()
        self._cfg_parser = parser

    def __del__(self):
        self.do_stop()
        self._log_writer.close_fd()

    def do_start(self) -> dict:
        """noblock"""
        if self._proc_lst:
            info = 'dst server is running, do nothing'
            log.info(info)
            return response(1, info=info)
        cfg = self._cfg_parser.read()
        self._init_cfg(cfg)
        self._proc_lst = self._run(cfg)
        return response(0)

    def do_stop(self, timeout=30) -> dict:
        """block"""

        if not self._proc_lst:
            log.info('dst server has stopped, do nothing')
            return response(0)

        for p in self._proc_lst:
            p.send_signal(2)

        start_time = time.time()
        is_run = True
        while is_run:
            cost_time = time.time() - start_time
            if cost_time > timeout:
                log.error('stop dst server timeout')
                for p in self._proc_lst:
                    p.kill()

            time.sleep(0.5)
            is_run = False
            for p in self._proc_lst:
                if p.poll() is None:
                    is_run = True

        self._proc_lst = []
        log.info('stop dst server success')
        return response(0)

    def do_restart(self) -> dict:
        log.info('begin restart')
        self.do_stop()
        self.do_start()
        log.info('restart success')
        return response(0)

    def do_update(self) -> dict:
        log.info('being update')
        is_running = bool(self._proc_lst)
        if is_running:
            self.do_stop()

        self.server_update(self._log_writer.get_fd())

        if is_running:
            self.do_start()
        log.info('update success')
        return response(0)

    def do_create_cluster(self) -> dict:
        log.info('being create_cluster')
        is_running = bool(self._proc_lst)
        if is_running:
            self.do_stop()

        cfg = self._cfg_parser.read()
        config.backup_cluster(cfg)
        config.create_cluster(cfg)

        if is_running:
            self.do_start()
        log.info('create_cluster success')
        return response(0)

    def do_mod_list(self) -> dict:
        log.info('begin mod_list')
        cfg = self._cfg_parser.read()
        mod_dict = config.read_modoverrides(cfg)
        mod_lst = list(mod_dict.keys())
        log.info(f'mod_list success: mod_list={mod_lst}')
        return response(0, mod_list=mod_lst)

    def do_mod_add(self, mod_lst: list = None, mod_overrides: str = None) -> dict:
        log.info('begin mod_add')
        is_running = bool(self._proc_lst)
        if is_running:
            self.do_stop()

        cfg = self._cfg_parser.read()
        if mod_lst is not None:
            new_mod_dict = {
                mod_id: '["workshop-%s"]={ configuration_options={ }, enabled=true }' % mod_id
                for mod_id in mod_lst
            }
            mod_dict = config.read_modoverrides(cfg)
            mod_dict.update(new_mod_dict)
        elif mod_overrides is not None:
            mod_dict = config.read_modoverrides(cfg, content=mod_overrides)
            if mod_dict == EXIT_FAILED:
                return response(1, info='invalid input')
        else:
            return response(1, info='no params get')
        config.save_modoverrides(cfg, mod_dict)

        if is_running:
            self.do_start()
        log.info('mod_add success')
        return response(0, mod_list=list(mod_dict.keys()))

    def do_mod_del(self, mod_lst: list = None) -> dict:
        log.info('begin mod_del')
        is_running = bool(self._proc_lst)
        if is_running:
            self.do_stop()

        cfg = self._cfg_parser.read()
        mod_dict = config.read_modoverrides(cfg)
        for mod_id in mod_lst:
            mod_dict.pop(mod_id, None)
        config.save_modoverrides(cfg, mod_dict)

        if is_running:
            self.do_start()
        log.info('mod_del success')
        return response(0, mod_list=list(mod_dict.keys()))

    def do_player_list(self, timeout=5) -> dict:
        """block"""
        if not self._proc_lst:
            return response(1, info='server is not running')

        log.info('begin get player_list')
        with ServerLogReader() as log_reader:
            master = self._proc_lst[0]
            master.stdin.write('BEGIN_INPUT\n')
            for proc in self._proc_lst:
                proc.stdin.write('c_listallplayers()\n')
            master.stdin.write('END_INPUT\n')

            start_time = time.time()
            pattern = re.compile(r'(?<=BEGIN_INPUT).*?(?=END_INPUT)', re.S)
            out = log_reader.read()
            while not pattern.search(out):
                cost_time = time.time() - start_time
                if cost_time > timeout:
                    info = 'get player list timeout'
                    log.error(f'{info}: out={out}')
                    return response(1, info=info)

                time.sleep(0.5)
                out += log_reader.read()
            msg = pattern.search(out).group()
            # todo 隐去 id
            player_lst = re.findall(r'\[[0-9]+?].+(?=\t)', msg)
            log.info(f'get play_list success: play_list={player_lst}')
            return response(0, player_list=player_lst)

    def do_say(self, msg: str) -> dict:
        """block"""
        log.info(f'say: {msg}')
        master = self._proc_lst[0]
        master.stdin.write(f'c_announce("{msg}")\n')
        return response(0)

    def _run(self, cfg) -> List[Popen]:
        cluster = config.get_cluster(cfg)
        if cfg['enable_64-bit']:
            cwd_path = f'{DST_HOME}/bin64'
            dst_path = f'{DST_HOME}/bin64/dontstarve_dedicated_server_nullrenderer_x64'
        else:
            cwd_path = f'{DST_HOME}/bin'
            dst_path = f'{DST_HOME}/bin/dontstarve_dedicated_server_nullrenderer'
        cmd = f'{dst_path} -console -cluster {cluster}'
        fd = self._log_writer.init_fd()

        log.info(f'start dst server, cluster={cluster}')
        _, master = run_cmd(f'{cmd} -shard Master', cwd=cwd_path, block=False, stdout=fd)
        proc_lst = [master]
        if cfg['enable_caves']:
            _, caves = run_cmd(f'{cmd} -shard Caves', cwd=cwd_path, block=False, stdout=fd)
            proc_lst.append(caves)
        return proc_lst

    @staticmethod
    def server_update(stdout=None):
        cmd = f'{STEAMCMD_HOME}/steamcmd.sh ' \
              f'+force_install_dir {DST_HOME} ' \
              f'+login anonymous ' \
              f'+app_update 343050 validate ' \
              f'+quit'
        run_cmd(cmd, stdout=stdout)

    @staticmethod
    def _init_cfg(cfg):
        cluster = config.get_cluster(cfg)
        cluster_path = config.get_cluster_path(cluster)
        if not os.path.exists(cluster_path):
            config.create_cluster(cfg)

        config.save_room_setting(cfg)
        config.save_world_setting(cfg)
        config.save_mod_setup(cfg)
        config.save_admin_lst(cfg)
        config.save_token(cfg)
