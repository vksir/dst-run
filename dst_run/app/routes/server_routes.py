import re

from dst_run.app.app import app
from dst_run.common.log import log
from dst_run.app.models.models import Ret
from dst_run.app.models.response_models import Response
from dst_run.common.asyncio_lock import lock
from dst_run.agent.agent import AGENT


def send_command(cmd: str, send_all=False) -> (int, str):
    ret, out = AGENT.run_cmd(cmd, send_all)
    log.info(f'run_cmd success: ret={ret}, out={out}')
    return ret, out


@app.get('/server/status', tags=['server'], response_model=Response, summary='获取饥荒服务器状态')
async def get_server_status():
    return Response(status=AGENT.status)


@app.get('/server/player-list', tags=['server'], response_model=Response, summary='显示在线玩家')
@lock
async def player_list():
    ret, out = send_command('c_listallplayers()', send_all=True)
    if ret:
        return Response(ret=Ret.FAILED, detail=out)
    players = re.findall(r'\[[0-9]+?].+(?=\t)', out)
    for i, player in enumerate(players):
        player = re.sub(r'\s*\(.+?\)\s*', ' ', player)
        player = re.sub(r'\s*<.+?>\s*', '', player)
        players[i] = player
    return Response(players=players)


@app.post('/server/announce/{msg}', tags=['server'], response_model=Response, summary='全服宣告')
@lock
async def announce(msg: str):
    ret, out = send_command(f'c_announce("{msg}")')
    return Response(ret=ret, detail=out)


@app.post('/server/{cmd}', tags=['server'], response_model=Response, summary='执行命令')
@lock
async def run_cmd(cmd: str):
    ret, out = send_command(cmd)
    return Response(ret=ret, detail=out)
