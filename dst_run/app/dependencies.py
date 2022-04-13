import json
from typing import List
import httpx
from fastapi import Header
from fastapi import Request
from fastapi import status
from fastapi import HTTPException
from fastapi import Depends
from dst_run.common.constants import Constants
from dst_run.common.log import log
from dst_run.confs.confs import CONF


def get_dependencies() -> List[Depends]:
    dependencies = []
    if CONF.common.authenticate_enable:
        dependencies.append(Depends(verify_token))
    return dependencies


ip_whitelist = CONF.common.authenticate_ip_whitelist
nickname = CONF.common.nickname
uuid = CONF.common.uuid
host = CONF.common.authenticate_host
port = CONF.common.authenticate_port


async def verify_token(request: Request, authorization: str = Header(...)):
    if request.client.host in ip_whitelist:
        return
    url = f'http://{host}:{port}/verify/{Constants.COMPONENT}'
    try:
        res = httpx.get(url, headers={'authorization': authorization}, params={
            'nickname': nickname,
            'uuid': uuid,
        })
    except Exception as e:
        log.error(f'verify_token failed: e={e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Unknown error')
    if res.status_code != 200:
        log.error(f'verify_token failed: status={res.status_code}, content={res.text}')
        detail = json.loads(res.text).get('detail', 'Signature verification failed')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
