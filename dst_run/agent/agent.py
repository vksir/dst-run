import re
import shlex
import subprocess
import time
import threading
from subprocess import Popen
from typing import List, Union

import functools
from typing.io import TextIO

from dst_run.common.log import log
from dst_run.common.constants import Constants
from dst_run.common.constants import FilePath
from dst_run.confs.confs import CONF
from dst_run.message_queue.msg_handler import MSG_QUEUE


__all__ = ['AGENT']


class Agent:
    STATUS_INACTIVE = 'INACTIVE'
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_UPDATE = 'UPDATING'

    def __init__(self):
        self._is_update = False
        self._running_processes: List[Popen] = []

        self._lock = threading.Lock()
        self._master_stdout_write: Union[TextIO, None] = None
        self._master_stdout_read: Union[TextIO, None] = None
        self._caves_stdout_write: Union[TextIO, None] = None
        self._caves_stdout_read: Union[TextIO, None] = None
        self._update_stdout_write: Union[TextIO, None] = None

    def __del__(self):
        try:
            self.stop()
            self._try_close_stdout()
        except Exception as e:
            log.error(f'del agent failed: e={e}')

    @property
    def status(self):
        if self._is_update:
            return self.STATUS_UPDATE
        return self.STATUS_ACTIVE if self._is_active else self.STATUS_INACTIVE

    def start(self) -> None:
        if self.status != self.STATUS_INACTIVE:
            return
        CONF.deploy()
        self._init_stdout()
        self._run()
        self._run_stdout_reader()

    def stop(self) -> None:
        if self.status != self.STATUS_ACTIVE:
            return
        self._stop()

    def restart(self) -> None:
        self.stop()
        self.start()

    def update(self) -> None:
        self._is_update = True
        is_active = self._is_active
        self.stop()

        self._init_stdout()
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

    def run_cmd(self, cmd: str, send_all=False) -> (int, str):
        if self.status != self.STATUS_ACTIVE:
            return Constants.RET_FAILED, f'server is {self.status.lower()}, do nothing'
        return self._run_cmd(cmd, send_all)

    @property
    def _is_active(self) -> bool:
        if not self._running_processes:
            return False
        if any(p.poll() is None for p in self._running_processes):
            return True
        self._running_processes = []
        return False

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

        master = self._run_process(f'{cmd} -shard Master', stdout=self._master_stdout_write, cwd=cwd_path)
        self._running_processes.append(master)
        if enable_caves:
            caves = self._run_process(f'{cmd} -shard Caves', stdout=self._caves_stdout_write, cwd=cwd_path)
            self._running_processes.append(caves)

    def _run_stdout_reader(self, period=0.1) -> None:
        def stdout_reader():
            log.info('start stdout_reader thread')
            lock = self._lock
            readline = self._master_stdout_read.readline
            sleep = functools.partial(time.sleep, period)
            processes_polls = [p.poll for p in self._running_processes]

            def is_active():
                return any(poll() is None for poll in processes_polls)

            def deal_stdout(out: str):
                special_msg = [
                    '[Join Announcement]',
                    '[Leave Announcement]',
                    '[Death Announcement]',
                    '[Resurrect Announcement]',
                    '[Say]',
                    '[Announcement]',
                    'Starting master server',
                    'Shutting down',
                    'Sim paused'
                ]
                if any(msg in out for msg in special_msg):
                    if out.endswith('\n'):
                        out = out[:-1]
                    MSG_QUEUE.produce(out)

            try:
                while is_active():
                    with lock:
                        line = readline()
                    if line:
                        deal_stdout(line)
                        continue
                    sleep()
            except Exception as e:
                log.error(f'exit stdout_reader thread: {e}')
                return
            log.info('exit stdout_reader thread')

        threading.Thread(target=stdout_reader).start()

    def _stop(self, timeout=30) -> None:
        for p in self._running_processes:
            p.send_signal(2)
        start_time = time.time()
        while self._is_active:
            cost_time = time.time() - start_time
            if cost_time > timeout:
                log.error('stop dst_server failed for timeout')
                break
            if cost_time > timeout - 5:
                log.error('stop dst_server too long, begin kill')
                for p in self._running_processes:
                    p.kill()
            time.sleep(0.5)

    def _update(self) -> None:
        cmd = f'{FilePath.STEAMCMD_DIR}/steamcmd.sh ' \
              f'+force_install_dir {FilePath.DST_DIR} ' \
              f'+login anonymous ' \
              f'+app_update 343050 validate ' \
              f'+quit'
        process = self._run_process(cmd, stdout=self._update_stdout_write)
        process.communicate()

    def __run_cmd(self, cmd: str, process: Popen, timeout=5):
        if not cmd.endswith('\n'):
            cmd = f'{cmd}\n'
        process.stdin.write('BEGIN_CMD\n')
        process.stdin.write(cmd)
        process.stdin.write('END_CMD\n')
        out = ''
        pattern = re.compile(r'BEGIN_CMD(.*?)END_CMD', re.S)
        start_time = time.time()
        while not pattern.search(out):
            if time.time() - start_time > timeout:
                return Constants.RET_FAILED, f'read rum_cmd output timeout: cmd={cmd}, out={out}'
            out += self._master_stdout_read.read()  # todo
            time.sleep(0.1)
        out = pattern.search(out).groups()[0]
        try:
            out = re.search(r'\n(.*)\n', out, re.S).groups()[0]
        except Exception as e:
            return Constants.RET_FAILED, f'regex output failed: out={out}, e={e}'
        return Constants.RET_SUCCEED, out

    def _run_cmd(self, cmd: str, send_all=False) -> (int, str):
        alive_processes = [p for p in self._running_processes if p.poll() is None]
        target_processes = alive_processes[0:1] if not send_all else alive_processes
        with self._lock:
            out = ''
            for p in target_processes:
                ret, tmp = self.__run_cmd(cmd, p)
                if ret:
                    return Constants.RET_FAILED, tmp
                out += tmp
        return Constants.RET_SUCCEED, out

    def _try_close_stdout(self):
        if self._master_stdout_write:
            self._master_stdout_write.close()
        if self._master_stdout_read:
            self._master_stdout_read.close()
        if self._caves_stdout_write:
            self._caves_stdout_write.close()
        if self._caves_stdout_read:
            self._caves_stdout_read.close()
        if self._update_stdout_write:
            self._update_stdout_write.close()

    def _init_stdout(self):
        self._try_close_stdout()
        self._master_stdout_write = open(FilePath.GAME_MASTER_LOG_PATH, 'w', encoding='utf-8')
        self._master_stdout_read = open(FilePath.GAME_MASTER_LOG_PATH, 'r', encoding='utf-8')
        self._caves_stdout_write = open(FilePath.GAME_CAVES_LOG_PATH, 'w', encoding='utf-8')
        self._caves_stdout_read = open(FilePath.GAME_CAVES_LOG_PATH, 'r', encoding='utf-8')
        self._update_stdout_write = open(FilePath.GAME_UPDATE_LOG_PATH, 'w', encoding='utf-8')

    @staticmethod
    def _run_process(cmd: str, stdout: TextIO, cwd: str = None) -> subprocess.Popen:
        cmd = shlex.split(cmd)
        p = subprocess.Popen(cmd, cwd=cwd, encoding='utf-8', bufsize=1,
                             stdout=stdout,
                             stderr=subprocess.STDOUT,
                             stdin=subprocess.PIPE)
        return p


AGENT = Agent()
