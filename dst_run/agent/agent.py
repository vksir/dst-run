import re
import queue
import threading
import functools
import time
import subprocess
import shlex
import logging

from dst_run.common.constants import Constants
from dst_run.app.models.models import Status
from dst_run.common.constants import GameLog
from dst_run.common.log import log
from dst_run.message_queue.msg_handler import MSG_QUEUE


HEALTH_CHECK_PERIOD = 3
LOG_HANDLE_PERIOD = 1
STOP_CHECK_PERIOD = 0.1
RUN_CMD_PERIOD = 0.1


class Agent:
    """管理单个进程，处理日志，执行命令"""

    def __init__(self, name: str, *, cmd: str, cwd: str, agent_log: logging.Logger):
        self.name = name
        self._cmd = cmd
        self._cwd = cwd
        self._process = None
        self._log = agent_log

        self._log_que = queue.Queue()
        self._cmd_que = queue.Queue()
        self._is_running_cmd = False
        self._cmd_lock = threading.Lock()

        self._status = Status.INACTIVE

    def __del__(self):
        self.stop(block=True)

    @property
    def status(self):
        """返回 Agent 状态"""
        return self._status

    @status.setter
    def status(self, value):
        log.info(f'change status from {self._status} to {value}')
        self._status = value

    @property
    def active(self):
        return self._process.poll() is None

    def run(self):
        log.info('begin run')
        self.status = Status.STARTING
        self._run()
        threading.Thread(target=self._loop_log_read,
                         name=self.name,
                         daemon=True).start()
        threading.Thread(target=self._loop_log_handle,
                         name=self.name,
                         daemon=True).start()
        threading.Thread(target=self.health_check,
                         name=self.name,
                         daemon=True).start()
        log.info('end run')

    def _run(self) -> None:
        self._process = subprocess.Popen(shlex.split(self._cmd),
                                         cwd=self._cwd,
                                         encoding='utf-8',
                                         bufsize=1,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT,
                                         stdin=subprocess.PIPE)

    def _loop_log_read(self):
        """阻塞读取日志，打印日志，并放入日志队列中"""

        log.info(f'start loop_log_read')
        try:
            while self.active:
                # 阻塞读取
                line = self._process.stdout.readline().strip()
                if not line:
                    continue
                self._log_que.put(line)
                self._log.info(line)
        except Exception as e:
            log.error(f'loop_log_read failed: {e}')
        log.info('stop loop_log_read')

    def _loop_log_handle(self):
        """无阻塞处理日志"""

        log.info('start loop_log_handle')
        while self.active or not self._log_que.empty():
            try:
                line = self._log_que.get(False)
            except queue.Empty:
                time.sleep(LOG_HANDLE_PERIOD)
                continue
            self._handle_log(line)
            if self._is_running_cmd:
                self._cmd_que.put(line)
        log.info('stop loop_log_handle')

    def health_check(self):
        log.info('begin health_check')
        while self.active:
            time.sleep(HEALTH_CHECK_PERIOD)
        self.status = Status.INACTIVE
        log.info('end health_check, process dead')

    def _handle_log(self, line: str):
        special_logs = GameLog.dict().values()
        if any(special_log in line for special_log in special_logs):
            MSG_QUEUE.produce(self.name, line)

        if GameLog.MASTER_ACTIVE in line:
            self.status = Status.ACTIVE

        if GameLog.CAVES_ACTIVE in line:
            self.status = Status.ACTIVE

    def run_cmd(self, cmd: str) -> (int, str):
        log.info(f'begin rum_cmd: process={self.name}, cmd={cmd}')
        with self._cmd_lock:
            self._is_running_cmd = True
            ret, output = self._run_cmd(cmd)
            self._is_running_cmd = False
            return ret, output

    def _run_cmd(self, cmd: str, timeout=5):
        self._process.stdin.write(f'BEGIN_CMD\n{cmd}\nEND_CMD\n')
        out = ''
        pattern = re.compile(r'BEGIN_CMD(.*?)END_CMD', re.S)
        start_time = time.time()
        while not pattern.search(out):
            if time.time() - start_time > timeout:
                log.error(f'read output timeout: process={self.name}, cmd={cmd}, out={out}')
                return Constants.RET_FAILED, out
            time.sleep(RUN_CMD_PERIOD)
            while not self._cmd_que.empty():
                out += self._cmd_que.get()
        out = pattern.search(out).groups()[0]
        log.info(f'run_cmd success: process={self.name}, cmd={cmd}, out={out}')
        return Constants.RET_SUCCEED, out

    def stop(self, block=False):
        log.info('begin stop')
        self.status = Status.STOPPING
        self._process.send_signal(2)
        if block:
            while self.active:
                time.sleep(STOP_CHECK_PERIOD)
        log.info('end stop')
