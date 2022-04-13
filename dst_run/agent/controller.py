import re
import shlex
import subprocess
import time
import threading
from subprocess import Popen
from typing import List, Union, Dict

import functools
from typing.io import TextIO

from dst_run.common.log import log
from dst_run.agent.process_log import process_log
from dst_run.common.constants import Constants
from dst_run.common.constants import FilePath
from dst_run.confs.confs import CONF
from dst_run.message_queue.msg_handler import MSG_QUEUE
from dst_run.agent.agent import Agent


__all__ = ['CONTROLLER']

from dst_run.reporter.reporter import REPORTER


class Controller:
    STATUS_INACTIVE = 'INACTIVE'
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_UPDATE = 'UPDATING'

    def __init__(self):
        self._is_update = False
        self._agents: Dict[str, Agent] = {}

    def __del__(self):
        try:
            self.stop()
        except Exception as e:
            log.error(f'del agent failed: e={e}')

    @property
    def _is_active(self):
        return any(agent.is_active() for agent in self._agents.values())

    @property
    def status(self):
        if self._is_update:
            return self.STATUS_UPDATE
        return self.STATUS_ACTIVE if self._is_active else self.STATUS_INACTIVE

    def start(self) -> None:
        if self.status != self.STATUS_INACTIVE:
            return
        CONF.deploy()
        self._run()

    def stop(self) -> None:
        if self.status != self.STATUS_ACTIVE:
            return
        threads = []
        for process_name, agent in self._agents.items():
            th = threading.Thread(target=agent.stop_process, name=process_name)
            th.start()
            threads.append(th)
        for th in threads:
            th.join()
        self._agents = {}

    def restart(self) -> None:
        self.stop()
        self.start()

    def update(self) -> None:
        self._is_update = True
        is_active = self._is_active
        self.stop()

        self._update()
        if is_active:
            self.start()
        self._is_update = False

    def regenerate(self):
        is_active = self._is_active
        self.stop()

        CONF.cluster.clean_cluster_save()
        if is_active:
            self.start()

    def run_cmd(self, cmd: str, process_name=Constants.MASTER) -> (int, str):
        if self.status != self.STATUS_ACTIVE:
            return Constants.RET_FAILED, f'server is {self.status.lower()}, do nothing'
        if process_name not in self._agents:
            return Constants.RET_FAILED, f'process_name {process_name} is not exists'
        return self._agents[process_name].run_cmd(cmd)

    def _run(self) -> None:
        enable_64bit = CONF.common.enable_64bit
        enable_caves = CONF.common.enable_caves
        if enable_64bit:
            cwd_path = f'{FilePath.DST_DIR}/bin64'
            dst_path = f'{FilePath.DST_DIR}/bin64/dontstarve_dedicated_server_nullrenderer_x64'
        else:
            cwd_path = f'{FilePath.DST_DIR}/bin'
            dst_path = f'{FilePath.DST_DIR}/bin/dontstarve_dedicated_server_nullrenderer'
        cmd = f'{dst_path} -console -cluster {FilePath.CLUSTER_NAME}'

        master = self._run_process(f'{cmd} -shard Master', cwd=cwd_path)
        master_agent = Agent(Constants.MASTER, master)
        master_agent.run()
        self._agents[Constants.MASTER] = master_agent
        if enable_caves:
            caves = self._run_process(f'{cmd} -shard Caves', cwd=cwd_path)
            caves_agent = Agent(Constants.CAVES, caves)
            caves_agent.run()
            self._agents[Constants.CAVES] = caves_agent

    def _update(self) -> None:
        cmd = f'{FilePath.STEAMCMD_DIR}/steamcmd.sh ' \
              f'+force_install_dir {FilePath.DST_DIR} ' \
              f'+login anonymous ' \
              f'+app_update 343050 validate ' \
              f'+quit'
        with open(FilePath.GAME_UPDATE_LOG_PATH, 'w', encoding='utf-8') as f:
            process = self._run_process(cmd, stdout=f)
            process.communicate()

    @staticmethod
    def _run_process(cmd: str, stdout: TextIO = subprocess.PIPE, cwd: str = None) -> subprocess.Popen:
        cmd = shlex.split(cmd)
        p = subprocess.Popen(cmd, cwd=cwd, encoding='utf-8', bufsize=1,
                             stdout=stdout,
                             stderr=subprocess.STDOUT,
                             stdin=subprocess.PIPE)
        return p


CONTROLLER = Controller()
