from dst_run.app.app import app
from dst_run.common.data_lib import DataLib
from dst_run.app.models.world_setting_models import Master
from dst_run.app.models.world_setting_models import Caves
from dst_run.app.models.response_models import Response
from dst_run.app.models.response_models import ResponseWorld
from dst_run.confs.confs import CONF
from dst_run.common.asyncio_lock import lock


@app.get('/world/master', tags=['world'], response_model=Response, summary='获取上世界设置')
async def get_master_world_setting():
    world = ResponseWorld(master=CONF.world.master)
    return Response(world=world)


@app.put('/world/master', tags=['world'], response_model=Response, summary='设置地上世界')
async def set_master_world_setting(master: Master):
    data = DataLib.filter_value_none(master.dict())
    data = DataLib.convert_value_to_str(data)
    CONF.world.update_master(data)
    CONF.save()
    return Response()


@app.get('/world/caves', tags=['world'], response_model=Response, summary='获取地下世界设置')
async def get_caves_world_setting():
    world = ResponseWorld(caves=CONF.world.caves)
    return Response(world=world)


@app.put('/world/caves', tags=['world'], response_model=Response, summary='设置地下世界')
async def set_caves_world_setting(caves: Caves):
    data = DataLib.filter_value_none(caves.dict())
    data = DataLib.convert_value_to_str(data)
    CONF.world.update_caves(data)
    CONF.save()
    return Response()
