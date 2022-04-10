import json
import time
import httpx
from fastapi import Request
from fastapi import Response
from fastapi import status
from dst_run.app.app import app
from dst_run.confs.confs import CONF
from dst_run.common.constants import Constants
from dst_run.common.log import log


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()

    if CONF.common.authenticate_enable and request.client.host != '127.0.0.1':
        print(request.client.host)
        token = request.headers.get('authorization')
        if token is None:
            return Response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={'content-type': 'application/json'},
                content=json.dumps({
                    'detail': 'No token found'
                }))
        is_verify_succeed = verify_token(token)
        if not is_verify_succeed:
            return Response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={'content-type': 'application/json'},
                content=json.dumps({
                    'detail': 'Unauthorized'
                }))
    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


def verify_token(token: str):
    try:
        nickname = CONF.common.nickname
        uuid = CONF.common.uuid
        host = CONF.common.authenticate_host
        port = CONF.common.authenticate_port
        url = f'http://{host}:{port}/verify/{Constants.COMPONENT}'
        res = httpx.get(url, headers={'Authorization': token}, params={
            'nickname': nickname,
            'uuid': uuid,
        })
        if res.status_code == 200:
            log.info('verify_token succeed')
            return True
        else:
            log.error(f'verify_token failed: status={res.status_code}, content={res.content}')
            return False
    except Exception as e:
        log.error(f'verify_token failed: e={e}')
        return False
