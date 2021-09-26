import json
from typing import List
from traceback import format_exc
from wsgiref.simple_server import make_server

from webob import Request, Response

import config
from log import log
from tools import run_cmd, get_choice, Executor
from constants import *
from controller import Controller, response


class Application:
    _cfg: dict = None
    _cluster: str = None

    def __init__(self):
        cfg_parser = config.CfgParser()
        self._controller = Controller(cfg_parser)

        cfg = cfg_parser.read()
        self._white_lst = cfg.get(WHITE_LIST_KEY)

    def __call__(self, env, start_response):
        req = Request(env)
        resp = Response()
        remote_addr = req.remote_addr
        body = req.body
        if remote_addr not in self._white_lst:
            resp.status_code = 401
            return resp(env, start_response)

        try:
            data = json.loads(body.decode())
        except Exception as e:
            info = 'json loads body failed'
            log.error(f'{info}: body={body}, remote_addr={remote_addr}, error={format_exc()}')
            resp.body = json.dumps(response(1, info=info)).encode()
            return resp(env, start_response)

        resp_data = self._deal_with_data(remote_addr, data)
        resp.body = json.dumps(resp_data).encode()
        return resp(env, start_response)

    def _deal_with_data(self, remote_addr: str, data: dict) -> dict:
        log.info(f'receive request: data={data}')
        method = data.get('method')

        if not method:
            info = 'get method failed'
            log.error(f'{info}: data={data}, remote_addr={remote_addr}')
            return response(1, info=info)

        method = 'do_' + method
        if not hasattr(self._controller, method):
            info = 'method not found'
            log.error(f'{info}: method={method}, data={data}, remote_addr={remote_addr}')
            return response(1, info=info)

        kwargs = data.get('kwargs', {})
        try:
            res = getattr(self._controller, method)(**kwargs)
            return res
        except Exception as e:
            info = 'run method failed'
            log.error(f'{info}: method={method}, data={data}, remote_addr={remote_addr}, error={format_exc()}')
            return response(1, info=info)


class HttpServer:
    def __init__(self, app, port=5800):
        self._app = app
        self._port = port

    def start(self):
        with make_server('', self._port, self._app) as httpd:
            print('dst_run http server start')
            httpd.serve_forever()

    @staticmethod
    def stop():
        file_name = os.path.split(__file__)[-1]
        log.debug(f'stop http server: file_name={file_name}')
        run_cmd("ps -ef | grep -v grep | grep %s | awk '{print $2}' | xargs kill -9" % file_name, shell=True)
