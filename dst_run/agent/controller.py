import logging
import shlex
import subprocess
import threading
from typing import Dict

from dst_run.common.log import log
from dst_run.common.constants import Constants
from dst_run.common.constants import FilePath
from dst_run.confs.confs import CONF
from dst_run.agent.agent import Agent
from dst_run.app.models.models import Status


class Controller:
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self.__status = None
        self._log = self._init_log()

    @property
    def status(self):
        """返回 Controller 状态"""

        if self._status is not None:
            return self._status

        status_lst = [agent.status for agent in self._agents.values()]
        status_info = {agent.name: agent.status.value.lower()
                       for agent in self._agents.values()}
        log.debug(f'current status: {status_info}')

        if all(status == Status.INACTIVE for status in status_lst):
            return Status.INACTIVE
        if Status.STOPPING in status_lst:
            return Status.STOPPING
        if Status.STARTING in status_lst:
            return Status.STARTING

        return Status.ACTIVE

    @property
    def status_str(self):
        return self.status.value.lower()

    @property
    def _status(self):
        return self.__status

    @_status.setter
    def _status(self, value):
        log.info(f'_status change from {self.__status} to {value}')
        self.__status = value

    def start(self) -> None:
        log.info('enter start')
        CONF.deploy()
        self._run()
        log.info('exit start')

    def _run(self) -> None:
        if CONF.common.enable_64bit:
            cwd_path = f'{FilePath.DST_DIR}/bin64'
            dst_path = f'{FilePath.DST_DIR}/bin64/dontstarve_dedicated_server_nullrenderer_x64'
        else:
            cwd_path = f'{FilePath.DST_DIR}/bin'
            dst_path = f'{FilePath.DST_DIR}/bin/dontstarve_dedicated_server_nullrenderer'
        cmd = f'{dst_path} -console -cluster {FilePath.CLUSTER_NAME}'

        master_agent = Agent(Constants.MASTER,
                             cmd=f'{cmd} -shard Master',
                             cwd=cwd_path,
                             agent_log=self._log)
        master_agent.run()
        self._agents[Constants.MASTER] = master_agent
        if CONF.common.enable_caves:
            caves_agent = Agent(Constants.CAVES,
                                cmd=f'{cmd} -shard Caves',
                                cwd=cwd_path,
                                agent_log=self._log)
            caves_agent.run()
            self._agents[Constants.CAVES] = caves_agent

    def stop(self, block=False) -> None:
        log.info('enter stop')
        threads = []
        for name, agent in self._agents.items():
            th = threading.Thread(target=agent.stop,
                                  args=(True,),
                                  name=name,
                                  daemon=True)
            th.start()
            threads.append(th)
        if block:
            for th in threads:
                th.join()
        self._agents = {}
        log.info('end stop')

    def restart(self) -> None:
        log.info('enter restart')
        self._status = Status.RESTARTING
        threading.Thread(target=self._restart,
                         daemon=True).start()

    def _restart(self):
        self.stop(block=True)
        self.start()
        self._status = None

    def update(self) -> None:
        log.info('enter update')
        self._status = Status.UPDATING
        threading.Thread(target=self._update,
                         daemon=True).start()

    def _update(self):
        self.stop(block=True)
        cmd = f'{FilePath.STEAMCMD_DIR}/steamcmd.sh ' \
              f'+force_install_dir {FilePath.DST_DIR} ' \
              f'+login anonymous ' \
              f'+app_update 343050 validate ' \
              f'+quit'
        cmd = shlex.split(cmd)
        with open(FilePath.GAME_UPDATE_LOG_PATH, 'w', encoding='utf-8') as f:
            subprocess.run(cmd, encoding='utf-8', bufsize=1,
                           stdout=f,
                           stderr=subprocess.STDOUT)
        self.start()
        self._status = None

    def regenerate(self):
        log.info('enter regenerate')
        self._status = Status.REGENERATING
        threading.Thread(target=self._regenerate,
                         daemon=True).start()

    def _regenerate(self):
        self.stop(block=True)
        CONF.cluster.clean_cluster_save()
        self.start()
        self._status = None

    def run_cmd(self, cmd: str, process_name=Constants.MASTER) -> (int, str):
        if self.status != Status.ACTIVE:
            return Constants.RET_FAILED, f'server is {self.status_str}, do nothing'
        if process_name not in self._agents:
            return Constants.RET_FAILED, f'process_name {process_name} is not exists'
        return self._agents[process_name].run_cmd(cmd)

    @staticmethod
    def _init_log():
        _log = logging.getLogger(__name__)
        _log.setLevel(logging.INFO)

        formatter = logging.Formatter('[%(asctime)s] [%(threadName)s] %(message)s')
        fh = logging.FileHandler(FilePath.GAME_LOG_PATH, 'w', encoding='utf-8')
        fh.setFormatter(formatter)
        fh.setLevel(logging.INFO)
        _log.addHandler(fh)
        return _log


CONTROLLER = Controller()
