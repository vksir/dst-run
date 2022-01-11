from asyncio import Lock
from functools import wraps
from typing import List
from fastapi import HTTPException, status

from dst_run import app
from dst_run.routes.models import *
from dst_run.routes.world_setting_models import Master, Caves
from dst_run.routes.config import Cfg
from dst_run.routes.controller import Controller


_lock = Lock()
cfg = Cfg()
ctr = Controller(cfg)


def lock(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        with _lock:
            res = f(*args, **kwargs)
        return res
    return wrapper


@lock
@app.post('/action/{action}', response_model=BaseResponse)
async def action(act: Action):
    if act == Action.START:
        resp = ctr.start()
    elif act == Action.STOP:
        resp = ctr.stop()
    elif act == Action.RESTART:
        resp = ctr.restart()
    elif act == Action.UPDATE:
        resp = ctr.update()
    else:
        raise Exception('invalid action type')
    return resp


@app.get('/room', tags=['room setting'], response_model=Room, summary='获取房间设置')
async def get_room_setting():
    return cfg.room.__root__


@lock
@app.put('/room', tags=['room setting'], response_model=BaseResponse, summary='设置房间')
async def set_room_setting(room: Room):
    cfg.room.__root__.update(filter_value_none(room.dict()))
    cfg.save_cfg()
    return BaseResponse(ret=Ret.SUCCESS)


@app.get('/world/master', tags=['world setting'], response_model=Master, summary='获取地上世界设置')
async def get_master_world_setting():
    return cfg.world.master


@lock
@app.put('/world/master', tags=['world setting'], response_model=BaseResponse, summary='设置地上世界')
async def set_master_world_setting(master: Master):
    cfg.world.master.update(filter_value_none(master.dict()))
    cfg.save_cfg()
    return BaseResponse(ret=Ret.SUCCESS)


@app.get('/world/caves', tags=['world setting'], response_model=Caves, summary='获取地下世界设置')
async def get_caves_world_setting():
    return cfg.world.caves


@lock
@app.put('/world/caves', tags=['world setting'], response_model=BaseResponse, summary='设置地下世界')
async def set_caves_world_setting(caves: Caves):
    cfg.world.caves.update(filter_value_none(caves.dict()))
    cfg.save_cfg()
    return BaseResponse(ret=Ret.SUCCESS)


@app.get('/world/master/template', tags=['world setting'], response_model=Data, summary='获取地上世界模板')
async def get_master_world_setting_template():
    pass


@app.put('/world/master/template', tags=['world setting'], response_model=BaseResponse, summary='设置地上世界模板')
async def set_world_setting_template(data: Data):
    pass


@app.get('/world/caves/template', tags=['world setting'], response_model=Data, summary='获取地下世界模板')
async def get_caves_world_setting_template():
    pass


@app.put('/world/caves/template', tags=['world setting'], response_model=BaseResponse, summary='设置地下世界模板')
async def set_caves_setting_template(data: Data):
    pass


@app.get('/mod', tags=['mod setting'], response_model=List[str], summary='获取 Mod 列表')
async def mod_list():
    return list(cfg.mod.__root__)


@app.get('/mod/show/{mod_id}', tags=['mod setting'], response_model=Mod, summary='获取 Mod 详细信息')
async def mod_show(mod_id: str):
    if mod_id not in cfg.mod.__root__:
        return HTTPException(status.HTTP_400_BAD_REQUEST, detail='invalid mod_id')
    return cfg.mod.__root__[mod_id]


@app.post('/mod', tags=['mod setting'], response_model=BaseResponse, summary='添加 Mod')
async def mod_add(data: Data):
    ret = cfg.mod.add_by_content(data.data)
    if ret:
        return HTTPException(status.HTTP_400_BAD_REQUEST, detail='mod_id not exists')
    return BaseResponse(ret=Ret.SUCCESS)


@app.delete('/mod', tags=['mod setting'], response_model=BaseResponse, summary='删除 Mod')
async def mod_del(mod_ids: List[str]):
    cfg.mod.delete(mod_ids)
    return BaseResponse(ret=Ret.SUCCESS)


@app.put('/mod/{mod_id}', tags=['mod setting'], summary='设置 Mod')
async def mod_modify(mod_id: str, mod: ModModify):
    if mod_id not in cfg.mod.__root__:
        return HTTPException(status.HTTP_400_BAD_REQUEST, detail='mod_id not exists')
    cfg.mod.__root__[mod_id].__dict__.update(filter_value_none(mod.dict()))
    return BaseResponse(ret=Ret.SUCCESS)


@app.get('/cluster', tags=['cluster'])
async def cluster_list():
    pass


@app.post('/cluster/{cluster_template_name}', tags=['cluster'])
async def cluster_create(cluster_template_name: str):
    pass


@app.delete('/cluster/{cluster_name}', tags=['cluster'])
async def cluster_del(cluster_name: str):
    pass


@app.put('/cluster/{cluster_name}', tags=['cluster'])
async def cluster_modify(cluster_name: str, name: str):
    pass


@app.post('/cluster/load/{cluster_name}', tags=['cluster'])
async def cluster_load(cluster_name):
    pass


@app.post('/cluster/upload', tags=['cluster'])
async def cluster_upload():
    pass


@app.get('/cluster/download/{cluster_name}', tags=['cluster'])
async def cluster_download(cluster_name: str):
    pass


@app.get('/cluster/template', tags=['cluster template'])
async def cluster_template_list():
    pass


@app.post('/cluster/template/{cluster_template_name}', tags=['cluster template'])
async def cluster_template_save(cluster_template_name: str):
    pass


@app.delete('/cluster/template/{cluster_template_name}', tags=['cluster template'])
async def cluster_template_del(cluster_template_name: str):
    pass


@app.put('/cluster/template/{cluster_template_name}', tags=['cluster template'])
async def cluster_template_modify(cluster_template_name: str, name: str):
    pass


@app.get('/cmd/player-list', tags=['cmd'])
async def player_list():
    pass


@app.post('/cmd/announce', tags=['cmd'])
async def announce():
    pass


@app.post('/cmd/{cmd}', tags=['cmd'])
async def run_cmd(cmd: str):
    pass


@app.get('/system/status', tags=['system'])
async def system_status():
    pass
