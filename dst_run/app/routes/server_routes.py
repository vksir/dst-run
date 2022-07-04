import re
from fastapi import APIRouter
from dst_run.common.constants import Constants
from dst_run.app.models.models import Ret
from dst_run.app.models.response_models import Response
from dst_run.common.asyncio_lock import lock
from dst_run.agent.controller import CONTROLLER


router = APIRouter(tags=['server'])


@router.get('/server/status', response_model=Response, summary='获取饥荒服务器状态')
async def get_server_status():
    return Response(status=CONTROLLER.status)


@router.get('/server/player_list', response_model=Response, summary='显示在线玩家')
@lock
async def player_list():
    ret, master_out = CONTROLLER.run_cmd('c_listallplayers()', process_name=Constants.MASTER)
    if ret:
        return Response(ret=Ret.FAILED, detail=f'master run_cmd failed: {master_out}')
    ret, caves_out = CONTROLLER.run_cmd('c_listallplayers()', process_name=Constants.CAVES)
    if ret:
        return Response(ret=Ret.FAILED, detail=f'caves run_cmd failed: {caves_out}')
    out = master_out + caves_out
    players = re.findall(r'\[\d+?\] \(.*?\) (.+?) ', out)
    return Response(players=players)


@router.post('/server/announce/{msg}', response_model=Response, summary='全服宣告')
@lock
async def announce(msg: str):
    ret, _ = CONTROLLER.run_cmd(f'c_announce("{msg}")')
    return Response(ret=ret)


@router.post('/server/regenerate_world', response_model=Response, summary='重新生成世界')
@lock
async def regenerate_world():
    ret, _ = CONTROLLER.run_cmd('c_regenerateworld()')
    return Response(ret=ret)


@router.post('/server/rollback/{days}', response_model=Response, summary='回档')
@lock
async def rollback(days: int):
    ret, _ = CONTROLLER.run_cmd(f'c_rollback({days})')
    return Response(ret=ret)


@router.post('/server/{cmd}', response_model=Response, summary='执行命令')
@lock
async def run_cmd(cmd: str):
    ret, results = CONTROLLER.run_cmd(cmd)
    return Response(ret=ret, detail=str(results))
