from typing import List
import httpx
from lxml import etree
from fastapi import Query
from fastapi import APIRouter
from fastapi import Body
from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from dst_run.common.data_lib import DataLib
from dst_run.app.models.models import Ret
from dst_run.app.models.models import Mod
from dst_run.app.models.response_models import Response
from dst_run.confs.confs import CONF


router = APIRouter(tags=['mod'])


class ModModify(BaseModel):
    id: str
    config: str = None
    remark: str = None
    enable: bool = None


@router.get('/mod', response_model=Response, summary='获取 Mod 列表')
async def mod_list():
    mods = CONF.mod.mods
    return Response(mods=mods)


@router.get('/mod/{mod_id}', response_model=Response, summary='获取 Mod 详细信息')
async def mod_show(mod_id: str):
    mod = CONF.mod.get_mod(mod_id)
    if mod is None:
        return Response(ret=Ret.FAILED, detail='mod_id not exists')
    return Response(mods=[mod])


@router.post('/mod', response_model=Response, summary='添加 Mod')
async def mod_add(body: str = Body(None, media_type='text/plain'), mod_ids: List[str] = Query(None, alias='mod_id')):
    if body:
        ret = CONF.mod.add_by_content(body)
        if ret:
            return Response(ret=Ret.FAILED, detail='invalid mod file content')
    if mod_ids:
        for mod_id in mod_ids:
            CONF.mod.add_by_mod_id(mod_id)
    CONF.save()
    return Response()


@router.delete('/mod', response_model=Response, summary='删除 Mod')
async def mod_del(mod_ids: List[str] = Query(..., alias='mod_id')):
    CONF.mod.delete_mod_by_ids(mod_ids)
    CONF.save()
    return Response()


@router.put('/mod', response_model=Response, summary='设置 Mod')
async def mod_modify(mods: List[ModModify]):
    mod_ids = [mod.id for mod in mods]
    not_exists_mod_ids = list(set(mod_ids) - set(CONF.mod.mod_ids))
    if not_exists_mod_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'mod_id not exists: {not_exists_mod_ids}')

    for mod in mods:
        mod_id = mod.id
        data = DataLib.filter_value_none(mod.dict())
        CONF.mod.update_mod(mod_id, data)
    CONF.save()
    return Response()


def get_mod_name_and_version(mod_id: str, proxy: str):
    try:
        url = f'https://steamcommunity.com/sharedfiles/filedetails/?id={mod_id}'
        res = httpx.get(url, proxies={'all://': proxy}, timeout=5)
    except httpx.TimeoutException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='steam community not responding')
    if res.status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='steam community access denied')

    html = etree.HTML(res.text)
    elements = html.xpath("//div[@class='workshopItemTitle']")
    element_texts = [ele.text for ele in elements]
    if len(element_texts) != 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='invalid mod id')
    name = element_texts[0]

    elements = html.xpath("//div[@class='workshopTags']//a")
    element_texts = [ele.text for ele in elements]
    if len(element_texts) != 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='invalid mod id')
    version = element_texts[0]
    return name, version


@router.post('/mod/info', response_model=Response, summary='自动获取 Mod 名称及版本')
async def update_mods_name_and_version(mod_ids: List[str] = Query(..., alias='mod_id')):
    not_exists_mod_ids = list(set(mod_ids) - set(CONF.mod.mod_ids))
    if not_exists_mod_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'mod_id not exists: {not_exists_mod_ids}')
    proxy = CONF.common.proxy
    if not proxy:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='proxy not configured')

    for mod_id in mod_ids:
        name, version = get_mod_name_and_version(mod_id, proxy)
        data = Mod(name=name, version=version).dict()
        data = DataLib.filter_value_none(data)
        CONF.mod.update_mod(mod_id, data)
    CONF.save()
    return Response()
