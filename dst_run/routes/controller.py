import re
import shlex
import subprocess
import threading
import time
import functools
from subprocess import Popen
from queue import Queue, Empty
from typing import List, Union
from typing.io import TextIO

from dst_run.common.log import log
from dst_run.common.constants import Constants
from dst_run.common.constants import FilePath
from dst_run.routes.config import Cfg
from dst_run.routes.models.response_models import Response


class Agent:
    def __init__(self, processes: List[Popen]):
        self._processes = processes
        self._lock = threading.Lock()
        self._stdout = open(FilePath.GAME_LOG_PATH, 'r', encoding='utf-8')

    def __del__(self):
        self._stdout.close()

    def _thread(self, period=0.1):
        log.info('start agent thread')
        lock = self._lock
        stdout = self._stdout
        sleep = functools.partial(time.sleep, period)

        def deal_stdout(out: str):
            pass

        while any(p.poll() is None for p in self._processes):
            with lock:
                line = stdout.readline()
            deal_stdout(line)
            sleep()
        log.info('exit agent thread')

    def run(self):
        thread = threading.Thread(target=self._thread, daemon=True)
        thread.start()

    def _run_cmd(self, cmd: str, process: Popen, timeout=5):
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
                log.error(f'read rum_cmd output timeout: cmd={cmd}, out={out}')
                return Constants.RET_FAILED, ''
            out += self._stdout.read()
            time.sleep(0.1)
        out = pattern.search(out).groups()[0]
        out = re.search(r'\n(.*)\n', out, re.S).groups()[0]
        return Constants.RET_SUCCEED, out

    def run_cmd(self, cmd: str, send_all=False):
        if not any(p.poll() is None for p in self._processes):
            log.info('no process running, run_cmd do nothing')
            return Constants.RET_FAILED, ''
        alive_processes = [p for p in self._processes if p.poll() is None]
        target_processes = alive_processes[0:1] if not send_all else alive_processes
        with self._lock:
            out = ''
            for p in target_processes:
                ret, tmp = self._run_cmd(cmd, p)
                if ret:
                    return Constants.RET_FAILED, ''
                out += tmp
        return Constants.RET_SUCCEED, out


class Controller:
    def __init__(self, cfg: Cfg):
        self._cfg = cfg
        self._processes: List[Popen] = []
        self._stdout: Union[TextIO, None] = None
        self._agent: Union[Agent, None] = None

    def __del__(self):
        try:
            self.stop()
        except NameError:
            pass
        if self._stdout:
            self._stdout.close()

    def start(self):
        """noblock"""
        if self.is_running:
            log.info('dst server is running, do nothing')
            return Response(ret=Constants.RET_SUCCEED,
                            detail='dst_server is running, do nothing')
        self._cfg.deploy()
        self._run()
        return Response(ret=Constants.RET_SUCCEED)

    def stop(self, timeout=30):
        """block"""
        if not self.is_running:
            return Response(ret=Constants.RET_SUCCEED,
                            detail='dst_server has stopped, do nothing')
        ret = self._stop(timeout)
        if ret:
            return Response(ret=Constants.RET_FAILED)
        return Response(ret=Constants.RET_SUCCEED)

    def restart(self):
        self.stop()
        self.start()
        return Response(ret=Constants.RET_SUCCEED)

    def update(self):
        is_running = self.is_running
        self.stop()
        self.update()
        if is_running:
            self.start()
        return Response(ret=Constants.RET_SUCCEED)

    def run_cmd(self, cmd: str):
        if not isinstance(self._agent, Agent):
            log.info('agent has not initialized, do nothing')
            return Constants.RET_FAILED, ''
        ret, out = self._agent.run_cmd(cmd)
        log.info(f'run_cmd success: ret={ret}, out={out}')
        return ret, out

    @property
    def is_running(self):
        return bool(self._processes)

    def _get_stdout(self):
        if self._stdout:
            self._stdout.close()
        self._stdout = open(FilePath.GAME_LOG_PATH, 'w', encoding='utf-8')
        return self._stdout

    def _run(self) -> (List[Popen], Queue, Queue):
        enable_64bit = self._cfg.common.get_enable_64bit()
        enable_caves = self._cfg.common.get_enable_caves()
        if enable_64bit:
            cwd_path = f'{FilePath.DST_DIR}/bin64'
            dst_path = f'{FilePath.DST_DIR}/bin64/dontstarve_dedicated_server_nullrenderer_x64'
        else:
            cwd_path = f'{FilePath.DST_DIR}/bin'
            dst_path = f'{FilePath.DST_DIR}/bin/dontstarve_dedicated_server_nullrenderer'
        cmd = f'{dst_path} -console -cluster {FilePath.CLUSTER_NAME}'
        stdout = self._get_stdout()

        master = self._run_process(f'{cmd} -shard Master', cwd=cwd_path, stdout=stdout)
        self._processes.append(master)
        if enable_caves:
            caves = self._run_process(f'{cmd} -shard Caves', cwd=cwd_path, stdout=stdout)
            self._processes.append(caves)
        self._agent = Agent(self._processes)
        self._agent.run()

    def _stop(self, timeout):
        for p in self._processes:
            p.send_signal(2)

        start_time = time.time()
        is_run = True
        while is_run:
            cost_time = time.time() - start_time
            if cost_time > timeout:
                log.error('stop dst_server failed for timeout')
                return Constants.RET_FAILED
            if cost_time > timeout - 5:
                log.error('stop dst_server too long, begin kill')
                for p in self._processes:
                    p.kill()
            time.sleep(0.5)
            is_run = any(p.poll() is None for p in self._processes)

        self._processes = []
        return Constants.RET_SUCCEED

    @staticmethod
    def _update():
        pass

    @staticmethod
    def _run_process(cmd: str, cwd: str, stdout: TextIO) -> subprocess.Popen:
        cmd = shlex.split(cmd)
        p = subprocess.Popen(cmd, cwd=cwd, encoding='utf-8', bufsize=1,
                             stdout=stdout,
                             stderr=subprocess.STDOUT,
                             stdin=subprocess.PIPE)
        return p
