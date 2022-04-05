from typing import List
from fastapi import Query
from dst_run.app.app import app
from dst_run.common.data_lib import DataLib
from dst_run.app.models.models import Ret
from dst_run.app.models.models import Mod
from dst_run.app.models.response_models import Response
from dst_run.confs.confs import CONF


@app.get('/mod', tags=['mod'], response_model=Response, summary='获取 Mod 列表')
async def mod_list():
    mods = CONF.mod.mods
    return Response(mods=mods)


@app.get('/mod/show/{mod_id}', tags=['mod'], response_model=Response, summary='获取 Mod 详细信息')
async def mod_show(mod_id: str):
    mod = CONF.mod.get_mod(mod_id)
    if mod is None:
        return Response(ret=Ret.FAILED, detail='mod_id not exists')
    return Response(mods=[mod])


@app.post('/mod', tags=['mod'], response_model=Response, summary='添加 Mod')
async def mod_add(content: str = None, mod_ids: List[str] = Query(None, alias='mod_id')):
    if content:
        ret = CONF.mod.add_by_content(content)
        if ret:
            return Response(ret=Ret.FAILED, detail='invalid mod file content')
    if mod_ids:
        for mod_id in mod_ids:
            CONF.mod.add_by_mod_id(mod_id)
    CONF.save()
    return Response()


@app.delete('/mod', tags=['mod'], response_model=Response, summary='删除 Mod')
async def mod_del(mod_ids: List[str]):
    CONF.mod.delete_backup_cluster(mod_ids)
    CONF.save()
    return Response()


@app.put('/mod/{mod_id}', tags=['mod'], response_model=Response, summary='设置 Mod')
async def mod_modify(mod_id: str, mod: Mod):
    data = DataLib.filter_value_none(mod.dict())
    data = DataLib.filter_key(data, ['id', 'name', 'version'])
    ret = CONF.mod.update_mod(mod_id, data)
    if ret:
        return Response(ret=Ret.FAILED, detail='mod_id not exists')
    CONF.save()
    return Response()
