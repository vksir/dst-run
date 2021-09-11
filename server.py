

import time
import threading

import config
import log
from constants import *


class Server:
    def run(self):
        while True:
            cfg = config.read_cfg()
            config.set_mod_setup(cfg)
            config.set_token(cfg)
            self._set_cluster_setting()

            proc_lst = self._run(cfg)
            self._stdout_handler(proc_lst)

            while True:
                if [p.poll() for p in proc_lst] != [None] * len(proc_lst):
                    log.error('server exit, try to start again')
                    break
                if time.localtime().tm_hour == 3:
                    log.info('begin update server')
                    for p in proc_lst:
                        p.send_signal(2)
                    for p in proc_lst:
                        p.wait()
                    self.server_update()
                    log.info('update server completely')
                    time.sleep(60 * 60)
                    break
                time.sleep(60 * 10)

    @staticmethod
    def _run(cfg):
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
        def tail(p, tag):
            count = 0
            while p.poll() is None:
                out = p.stdout.readline()
                if not out:
                    count += 1
                    if count > 10:
                        log.error(f'no out for too many times: count={count}')
                        exit(1)
                print(f'{tag}:\t{out}', end='')

        for i in range(len(proc_lst)):
            threading.Thread(target=tail,
                             args=(proc_lst[i], 'Master' if i == 0 else 'Caves'),
                             daemon=True).start()

    @staticmethod
    def server_update():
        run_cmd(f'{STEAMCMD_HOME}/steamcmd.sh '
                f'+force_install_dir {DST_HOME} '
                f'+login anonymous '
                f'+app_update 343050 validate '
                f'+quit')
