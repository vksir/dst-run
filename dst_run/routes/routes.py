from asyncio import Lock
from functools import wraps
from typing import List
from fastapi import HTTPException, status, Query

from dst_run.app import app
from dst_run.common.data_lib import DataLib
from dst_run.routes.models.models import *
from dst_run.routes.models.response_models import Response
from dst_run.routes.models.world_setting_models import Master, Caves
from dst_run.routes.config import Cfg
from dst_run.routes.controller import Controller


_lock = Lock()
cfg = Cfg()
controller = Controller(cfg)


def lock(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        await _lock.acquire()
        res = await f(*args, **kwargs)
        _lock.release()
        return res
    return wrapper


@app.post('/action/{action}', response_model=Response)
@lock
async def action(act: Action):
    mapping = {
        act.START: controller.start,
        act.STOP: controller.stop,
        act.RESTART: controller.restart,
        act.UPDATE: controller.update
    }
    if act not in mapping:
        return Response(ret=Ret.FAILED, detail='invalid action type')
    func = mapping[act]
    return func()


@app.get('/room', tags=['room setting'], response_model=Response, summary='获取房间设置')
async def get_room_setting():
    return Response(room=cfg.room.get_room())


@app.put('/room', tags=['room setting'], response_model=Response, summary='设置房间')
@lock
async def set_room_setting(room: Room):
    data = DataLib.filter_value_none(room.dict())
    data = DataLib.convert_value_to_str(data)
    cfg.room.update(data)
    cfg.save()
    return Response()


@app.get('/world/master', tags=['world setting'], response_model=Master, summary='获取地上世界设置')
async def get_master_world_setting():
    return Response(master=cfg.world.get_master())


@app.put('/world/master', tags=['world setting'], response_model=Response, summary='设置地上世界')
@lock
async def set_master_world_setting(master: Master):
    data = DataLib.filter_value_none(master.dict())
    data = DataLib.convert_value_to_str(data)
    cfg.world.update_master(data)
    cfg.save()
    return Response()


@app.get('/world/caves', tags=['world setting'], response_model=Caves, summary='获取地下世界设置')
async def get_caves_world_setting():
    return Response(caves=cfg.world.get_caves())


@app.put('/world/caves', tags=['world setting'], response_model=Response, summary='设置地下世界')
@lock
async def set_caves_world_setting(caves: Caves):
    data = DataLib.filter_value_none(caves.dict())
    data = DataLib.convert_value_to_str(data)
    cfg.world.update_caves(data)
    cfg.save()
    return Response()


@app.get('/world/master/template', tags=['world setting'], response_model=Response, summary='获取地上世界模板')
async def get_master_world_setting_template():
    pass


@app.put('/world/master/template', tags=['world setting'], response_model=Response, summary='设置地上世界模板')
async def set_world_setting_template(content: str):
    pass


@app.get('/world/caves/template', tags=['world setting'], response_model=Response, summary='获取地下世界模板')
async def get_caves_world_setting_template():
    pass


@app.put('/world/caves/template', tags=['world setting'], response_model=Response, summary='设置地下世界模板')
async def set_caves_setting_template(content: str):
    pass


@app.get('/mod', tags=['mod setting'], response_model=Response, summary='获取 Mod 列表')
async def mod_list():
    mods = cfg.mod.get_mods()
    return Response(mods=mods)


@app.get('/mod/show/{mod_id}', tags=['mod setting'], response_model=Response, summary='获取 Mod 详细信息')
async def mod_show(mod_id: str):
    mod = cfg.mod.get_mod(mod_id)
    if mod is None:
        return Response(ret=Ret.FAILED, detail='mod_id not exists')
    return Response(mods=[mod])


@app.post('/mod', tags=['mod setting'], response_model=Response, summary='添加 Mod')
async def mod_add(content: str = None, mod_ids: List[str] = Query(None)):
    if content:
        ret = cfg.mod.add_by_content(content)
        if ret:
            return Response(ret=Ret.FAILED, detail='invalid mod file content')
    if mod_ids:
        for mod_id in mod_ids:
            cfg.mod.add_by_mod_id(mod_id)
    cfg.save()
    return Response()


@app.delete('/mod', tags=['mod setting'], response_model=Response, summary='删除 Mod')
async def mod_del(mod_ids: List[str]):
    cfg.mod.delete_backup_cluster(mod_ids)
    cfg.save()
    return Response()


@app.put('/mod/{mod_id}', tags=['mod setting'], response_model=Response, summary='设置 Mod')
async def mod_modify(mod_id: str, mod: Mod):
    data = DataLib.filter_value_none(mod.dict())
    data = DataLib.filter_key(data, ['id', 'name', 'version'])
    ret = cfg.mod.update_mod(mod_id, data)
    if ret:
        return Response(ret=Ret.FAILED, detail='mod_id not exists')
    cfg.save()
    return Response()


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
async def cluster_rename(cluster_name: str, name: str):
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


@app.post('/cmd/{cmd}', tags=['cmd'], response_model=Response)
async def run_cmd(cmd: str):
    ret, out = controller.run_cmd(cmd)
    return Response(ret=ret, detail=out)


@app.get('/system/status', tags=['system'])
async def system_status():
    pass
