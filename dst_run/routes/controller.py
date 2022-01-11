import shlex
import subprocess
import time
from subprocess import Popen
from threading import Thread
from queue import Queue, Empty
from typing import List, Union
from typing.io import TextIO

from dst_run import log
from dst_run.common.constants import *
from dst_run.routes.config import Cfg
from dst_run.routes.models import *


BEGIN_CMD = 'BEGIN_CMD'
END_CMD = 'END_CMD'


def run_process(cmd: str, cwd: str, stdout: TextIO) -> (int, subprocess.Popen):
    cmd = shlex.split(cmd)
    p = subprocess.Popen(cmd, cwd=cwd, encoding='utf-8', bufsize=1,
                         stdout=stdout,
                         stderr=subprocess.STDOUT,
                         stdin=subprocess.PIPE)
    return p


class RPCRequest(BaseModel):
    method: str
    args: list = []
    kwargs: dict = {}


class RPCResponse(BaseResponse):
    ret: Ret
    detail: str = ''


class LogHandler(Thread):
    def __init__(self, proc_lst: List[Popen],
                 send_que: Queue,
                 recv_que: Queue,
                 period=0.1):
        super().__init__()
        self._proc_lst = proc_lst
        self._send_que = send_que
        self._recv_que = recv_que
        self._period = period

    def run(self) -> None:
        log.info('start log handler')
        with open(GAME_LOG_PATH, 'r', encoding='utf-8') as f:
            while any(p.poll() is None for p in self._proc_lst):
                pass


class Controller:
    def __init__(self, cfg: Cfg):
        self._cfg = cfg
        self._proc_lst: List[Popen] = []
        self._send_que: Union[Queue, None] = None
        self._recv_que: Union[Queue, None] = None
        self._log_writer: Union[TextIO, None] = None

    def __del__(self):
        try:
            self.stop()
        except NameError:
            pass
        if self._log_writer:
            self._log_writer.close()

    def start(self):
        """noblock"""
        if self.is_running:
            log.info('dst server is running, do nothing')
            return BaseResponse(ret=Ret.SUCCESS,
                                detail='dst_server is running, do nothing')
        self._cfg.deploy()
        self._proc_lst, self._send_que, self._recv_que = self._run()
        return BaseResponse(ret=Ret.SUCCESS)

    def stop(self, timeout=30):
        """block"""
        if not self.is_running:
            return BaseResponse(ret=Ret.SUCCESS,
                                detail='dst_server has stopped, do nothing')

        for p in self._proc_lst:
            p.send_signal(2)

        start_time = time.time()
        is_run = True
        while is_run:
            cost_time = time.time() - start_time
            if cost_time > timeout:
                log.error('stop dst_server timeout, begin kill')
                for p in self._proc_lst:
                    p.kill()
            time.sleep(0.5)
            is_run = any(p.poll() is None for p in self._proc_lst)

        self._proc_lst = []
        log.info('stop dst_server success')
        return BaseResponse(ret=Ret.SUCCESS)

    def restart(self):
        self.stop()
        self.start()
        return BaseResponse(ret=Ret.SUCCESS)

    def update(self):
        is_running = self.is_running
        self.stop()
        self.update()
        if is_running:
            self.start()
        return BaseResponse(ret=Ret.SUCCESS)

    def rpc(self, method: str, args: list = None, kwargs: dict = None, timeout=5):
        log.info(f'begin rpc request: method={method}, args={args}, kwargs={kwargs}')
        args = args or []
        kwargs = kwargs or {}

        while not self._recv_que.empty():
            self._recv_que.get()
        self._send_que.put(RPCRequest(method=method, args=args, kwargs=kwargs))
        try:
            res: RPCResponse = self._recv_que.get(timeout=timeout)
        except Empty:
            return BaseResponse(ret=Ret.FAILED,
                                detail='run_cmd timeout')
        return BaseResponse(**res.dict())

    @property
    def is_running(self):
        return bool(self._proc_lst)

    def _run(self) -> (List[Popen], Queue, Queue):
        cluster = CLUSTER_NAME
        if self._cfg.server.enable_64bit:
            cwd_path = f'{DST_DIR}/bin64'
            dst_path = f'{DST_DIR}/bin64/dontstarve_dedicated_server_nullrenderer_x64'
        else:
            cwd_path = f'{DST_DIR}/bin'
            dst_path = f'{DST_DIR}/bin/dontstarve_dedicated_server_nullrenderer'
        cmd = f'{dst_path} -console -cluster {cluster}'

        if self._log_writer:
            self._log_writer.close()
        self._log_writer = open(GAME_LOG_PATH, 'w', encoding='utf-8')
        master = run_process(f'{cmd} -shard Master', cwd=cwd_path, stdout=self._log_writer)
        proc_lst = [master]
        if self._cfg.server.enable_caves:
            caves = run_process(f'{cmd} -shard Caves', cwd=cwd_path, stdout=self._log_writer)
            proc_lst.append(caves)

        send_que, recv_que = Queue(), Queue()
        log_handler = LogHandler(proc_lst, send_que=recv_que, recv_que=send_que)
        log_handler.start()
        return proc_lst, send_que, recv_que

    @staticmethod
    def _update():
        pass
