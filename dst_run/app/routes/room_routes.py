from fastapi import APIRouter
from dst_run.common.data_lib import DataLib
from dst_run.app.models.models import Room
from dst_run.app.models.response_models import Response
from dst_run.confs.confs import CONF


router = APIRouter(tags=['room'])


@router.get('/room', summary='获取房间设置')
async def get_room_setting():
    return Response(room=CONF.room.room)


@router.put('/room', summary='设置房间')
async def set_room_setting(room: Room):
    data = DataLib.filter_value_none(room.dict())
    data = DataLib.convert_value_to_str(data)
    CONF.room.update_room(data)
    CONF.save()
    return Response()
