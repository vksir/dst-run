import time
import threading
from typing import List
from subprocess import Popen

import config
import log
from constants import *
from tools import run_cmd


INTERVAL = 60


class Server:
    def __init__(self):
        self._lock = threading.Lock()

    def run(self):
        while True:
            cfg = config.read_cfg()
            self._init_cfg(cfg)

            proc_lst = self._run(cfg)
            self._stdout_handler(proc_lst)
            self._health_check(proc_lst)

    def _health_check(self, proc_lst: List[Popen]):
        while True:
            for proc in proc_lst:
                if proc.poll() is not None:
                    self.safe_exit(proc_lst)
                    log.error('server exit, start again after 30s')
                    return
            if time.localtime().tm_hour == 3:
                log.info('begin update server')
                self.safe_exit(proc_lst)
                self.server_update()
                log.info('update server completely')
                time.sleep(60 * 60)
                return
            time.sleep(INTERVAL)

    @staticmethod
    def _run(cfg) -> List[Popen]:
        cluster = config.get_cluster(cfg)
        if cfg['enable_64-bit']:
            dst_path = f'{DST_HOME}/bin64/dontstarve_dedicated_server_nullrenderer_x64'
        else:
            dst_path = f'{DST_HOME}/bin/dontstarve_dedicated_server_nullrenderer'
        cmd = f'{dst_path} -console -cluster {cluster}'

        log.info(f'start dst server, cluster={cluster}')
        proc_lst = [run_cmd(f'{cmd} -shard Master', cwd=f'{DST_HOME}/bin64', block=False)]
        if cfg['enable_caves']:
            proc_lst.append(run_cmd(f'{cmd} -shard Caves', cwd=f'{DST_HOME}/bin64', block=False))
        return proc_lst

    @staticmethod
    def _stdout_handler(proc_lst):
        def tail(p: Popen, tag):
            while p.poll() is None:
                out = p.stdout.readline()
                if not out:
                    log.error(f'no stdout')
                    continue
                print(f'{tag}:\t{out}', end='')

        for i, proc in enumerate(proc_lst):
            threading.Thread(target=tail,
                             args=(proc, 'Master' if i == 0 else 'Caves'),
                             daemon=True).start()

    @staticmethod
    def safe_exit(proc_lst: List[Popen]):
        for p in proc_lst:
            p.send_signal(2)
        for p in proc_lst:
            p.wait()

    @staticmethod
    def server_update():
        cmd_lst = [f'{STEAMCMD_HOME}/steamcmd.sh '
                   f'+force_install_dir {DST_HOME} '
                   f'+login anonymous '
                   f'+app_update 343050 validate '
                   f'+quit']
        for cmd in cmd_lst:
            run_cmd(cmd)

    @staticmethod
    def _init_cfg(cfg):
        config.save_room_setting(cfg)
        config.save_world_setting(cfg)
        config.save_mod_setup(cfg)
        config.save_admin_lst(cfg)
        config.save_token(cfg)
