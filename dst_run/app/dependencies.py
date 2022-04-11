import httpx
from fastapi import Header
from fastapi import Request
from fastapi import status
from fastapi import HTTPException
from dst_run.common.constants import Constants
from dst_run.common.log import log
from dst_run.confs.confs import CONF


enable = CONF.common.authenticate_enable
ip_whitelist = CONF.common.authenticate_ip_whitelist
nickname = CONF.common.nickname
uuid = CONF.common.uuid
host = CONF.common.authenticate_host
port = CONF.common.authenticate_port


async def verify_token(request: Request, authorization: str = Header(...)):
    if not enable or request.client.host in ip_whitelist:
        return
    try:
        url = f'http://{host}:{port}/verify/{Constants.COMPONENT}'
        res = httpx.get(url, headers={'authorization': authorization}, params={
            'nickname': nickname,
            'uuid': uuid,
        })
        if res.status_code != 200:
            log.error(f'verify_token failed: status={res.status_code}, content={res.content}')
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    except Exception as e:
        log.error(f'verify_token failed: e={e}')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
