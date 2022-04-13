import re
import queue
import threading
import functools
import time
from subprocess import Popen
from dst_run.common.constants import Constants
from dst_run.common.log import log
from dst_run.agent.process_log import process_log
from dst_run.message_queue.msg_handler import MSG_QUEUE


class Agent:
    def __init__(self, process_name: str, process: Popen, period=0.1):
        self.name = process_name
        self._process = process
        self._period = period
        self._log_que = queue.Queue()
        self._lock = threading.Lock()

    def is_active(self):
        return self._process.poll() is None

    def run(self):
        self._start_log_reader()
        self._start_log_handler()

    def _start_log_reader(self):
        def thread():
            log.info(f'start log_reader thread')
            readline = self._process.stdout.readline
            is_active = self.is_active
            put = self._log_que.put

            try:
                while is_active():
                    line = readline()[:-1]
                    if not line:
                        continue
                    put(line)
                    process_log.info(line)
            except Exception as e:
                log.error(f'log_reader failed: {e}')
            log.info('exit log_reader thread')
        threading.Thread(target=thread, name=self.name).start()

    def _start_log_handler(self):
        def thread():
            log.info('start log_handler thread')
            is_empty = self._log_que.empty
            get = functools.partial(self._log_que.get, False)
            sleep = functools.partial(time.sleep, self._period)
            handle_log = self._handle_log
            lock = self._lock
            is_active = self.is_active
            empty_exception = queue.Empty
            while is_active() or not is_empty():
                try:
                    with lock:
                        line = get()
                except empty_exception:
                    sleep()
                    continue
                handle_log(line)
            log.info('exit log_handler thread')
        threading.Thread(target=thread, name=self.name).start()

    def _handle_log(self, line: str):
        special_msg = [
            '[Join Announcement]',
            '[Leave Announcement]',
            '[Death Announcement]',
            '[Resurrect Announcement]',
            '[Say]',
            '[Announcement]',
            'Starting master server',
            'Sim paused',
            'Shutting down'
        ]
        if any(msg in line for msg in special_msg):
            MSG_QUEUE.produce(self.name, line)

    def run_cmd(self, cmd: str) -> (int, str):
        log.info(f'begin rum_cmd: process={self.name}, cmd={cmd}')
        with self._lock:
            log.debug(f'run_cmd acquire lock success: process={self.name}, cmd={cmd}')
            return self._run_cmd(cmd)

    def _run_cmd(self, cmd: str, period=0.1, timeout=5):
        self._process.stdin.write(f'BEGIN_CMD\n{cmd}\nEND_CMD\n')
        out = ''
        pattern = re.compile(r'BEGIN_CMD(.*?)END_CMD', re.S)
        start_time = time.time()
        while not pattern.search(out):
            if time.time() - start_time > timeout:
                log.error(f'read output timeout: process={self.name}, cmd={cmd}, out={out}')
                return Constants.RET_FAILED, out
            time.sleep(period)
            while not self._log_que.empty():
                out += self._log_que.get()
        out = pattern.search(out).groups()[0]
        log.info(f'run_cmd success: process={self.name}, cmd={cmd}, out={out}')
        return Constants.RET_SUCCEED, out

    def stop_process(self, timeout=30):
        log.info('begin stop process')
        self._process.send_signal(2)
        start_time = time.time()
        while self.is_active():
            cost_time = time.time() - start_time
            if cost_time > timeout:
                log.error('stop_process failed for timeout')
                break
            if cost_time > timeout - 5:
                log.error('stop_all_process too long, begin kill')
                self._process.kill()
                time.sleep(1)
            time.sleep(0.5)
        log.info('exit stop process')
