from fastapi import APIRouter, Body
from dst_run.app.models.response_models import Response
from dst_run.app.models.response_models import ResponseWorld
from dst_run.confs.confs import CONF


router = APIRouter(tags=['world'])


@router.get('/world/master', response_model=Response, summary='获取上世界设置')
async def get_master_world_setting():
    world = ResponseWorld(master=CONF.world.master)
    return Response(world=world)


@router.put('/world/master', response_model=Response, summary='设置地上世界')
async def set_master_world_setting(master: str = Body(None, media_type='text/plain')):
    CONF.world.update_master(master)
    return Response()


@router.get('/world/caves', response_model=Response, summary='获取地下世界设置')
async def get_caves_world_setting():
    world = ResponseWorld(caves=CONF.world.caves)
    return Response(world=world)


@router.put('/world/caves', response_model=Response, summary='设置地下世界')
async def set_caves_world_setting(caves: str = Body(None, media_type='text/plain')):
    CONF.world.update_caves(caves)
    return Response()
