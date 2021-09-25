import io
import re
import time
import threading
from threading import Thread
from typing import List, IO
from subprocess import Popen
from queue import Queue
from contextlib import ContextDecorator

import config
from log import log
from config import ServerLogWriter, ServerLogReader
from constants import *
from tools import run_cmd


INTERVAL = 60


def response(return_code: int, info: str = '', player_list: List[str] = None) -> dict:
    return dict(
        return_code=return_code,
        info=info,
        player_list=player_list if player_list else []
    )


class Controller:
    def __init__(self):
        self._proc_lst: List[Popen] = []
        self._log_writer = ServerLogWriter()

    def __del__(self):
        self.do_stop()
        self._log_writer.close_fd()

    def do_start(self) -> dict:
        """noblock"""
        if self._proc_lst:
            info = 'dst server is running, do nothing'
            log.info(info)
            return response(1, info=info)
        cfg = config.read_cfg()
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
        self.do_stop()
        self.do_start()
        return response(0)

    def do_update(self) -> dict:
        self.do_stop()
        self.server_update(self._log_writer.get_fd())
        self.do_start()
        return response(0)

    def do_new_cluster(self):
        self.do_stop()
        cfg = config.read_cfg()
        config.backup_cluster(cfg)
        config.create_cluster(cfg)
        self.do_start()

    def do_add_mods(self, mod_list=None, mod_overrides=None):
        pass

    def do_del_mods(self, mod_list=None):
        pass

    def do_player_list(self, timeout=5) -> dict:
        """block"""
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
            player_lst = re.findall(r'\[[0-9]+?\].+(?=\t)', msg)
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
        config.save_room_setting(cfg)
        config.save_world_setting(cfg)
        config.save_mod_setup(cfg)
        config.save_admin_lst(cfg)
        config.save_token(cfg)
        cluster = config.get_cluster(cfg)
        cluster_path = config.get_cluster_path(cluster)
        if not os.path.exists(cluster_path):
            config.create_cluster(cfg)
