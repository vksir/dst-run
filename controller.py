import re
import time
from typing import List
from subprocess import Popen

from dst_run.app.routes import config
from dst_run.common.log import log
from dst_run.app.routes import ServerLogWriter, ServerLogReader
from constants import *
from tools import run_cmd

INTERVAL = 60


class Controller:
    def __init__(self, parser: config.CfgParser):
        self._proc_lst: List[Popen] = []
        self._log_writer = ServerLogWriter()
        self._cfg_parser = parser

    def __del__(self):
        self.do_stop()
        self._log_writer.close_fd()

    def do_create_cluster(self) -> dict:
        log.info('being create_cluster')
        if self._is_running:
            self.do_stop()

        cfg = self._cfg_parser.read()
        config.backup_cluster(cfg)
        config.create_cluster(cfg)

        log.info('create_cluster success')
        return self._response(0)

    def do_mod_list(self) -> dict:
        log.info('begin mod_list')
        cfg = self._cfg_parser.read()
        mod_dict = config.read_modoverrides(cfg)
        mod_lst = list(mod_dict.keys())
        log.info(f'mod_list success: mod_list={mod_lst}')
        return self._response(0, mod_list=mod_lst)

    def do_mod_add(self, mod_lst: list = None, mod_overrides: str = None) -> dict:
        log.info('begin mod_add')
        is_running = self._is_running
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
            mod_dict = config.read_modoverrides(cfg)
            new_mod_dict = config.read_modoverrides(cfg, content=mod_overrides)
            if new_mod_dict == EXIT_FAILED:
                return self._response(1, info='invalid input')
            mod_dict.update(new_mod_dict)
        else:
            return self._response(1, info='no params get')
        config.save_modoverrides(cfg, mod_dict)

        if is_running:
            self.do_start()
        log.info('mod_add success')
        return self._response(0, mod_list=list(mod_dict.keys()))

    def do_mod_del(self, mod_lst: list = None) -> dict:
        log.info('begin mod_del')
        is_running = self._is_running
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
        return self._response(0, mod_list=list(mod_dict.keys()))

    def do_player_list(self, timeout=5) -> dict:
        """block"""
        if not self._is_running:
            return self._response(1, info='server is not running')

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
                    return self._response(1, info=info)

                time.sleep(0.5)
                out += log_reader.read()
            msg = pattern.search(out).group()
            player_lst = re.findall(r'\[[0-9]+?].+(?=\t)', msg)
            for i, player in enumerate(player_lst):
                player = re.sub(r'\s*\(.+?\)\s*', ' ', player)
                player = re.sub(r'\s*<.+?>\s*', '', player)
                player_lst[i] = player
            log.info(f'get play_list success: play_list={player_lst}')
            return self._response(0, player_list=player_lst)

    def do_say(self, msg: str) -> dict:
        """block"""
        if not self._is_running:
            return self._response(1, info='server is not running')

        log.info(f'say: {msg}')
        master = self._proc_lst[0]
        master.stdin.write(f'c_announce("{msg}")\n')
        return self._response(0)

    def do_run_cmd(self, msg: str):
        """noblock"""
        if not self._is_running:
            return self._response(1, info='server is not running')

        log.info(f'run_cmd: {msg}')
        master = self._proc_lst[0]
        master.stdin.write(f'{msg}\n')
        return self._response(0)

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

    def _response(self,
                  ret: int,
                  info: str = None,
                  player_list: list = None,
                  mod_list: list = None) -> dict:

        if info is None:
            info = 'server is running' if self._is_running else 'server has stopped'
        data = locals()
        data.pop('self', None)
        return data

    @property
    def _is_running(self):
        return bool(self._proc_lst)

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
