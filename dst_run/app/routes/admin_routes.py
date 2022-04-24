from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status
from dst_run.confs.confs import CONF
from dst_run.app.models.response_models import Response


router = APIRouter(tags=['admin'])


@router.get('/admin', response_model=Response, summary='获取管理员')
async def get_admins():
    return Response(admins=CONF.cluster.admins)


@router.post('/admin/{admin}', response_model=Response, summary='添加管理员')
async def add_admin(admin: str):
    CONF.cluster.admins.append(admin)
    CONF.save()
    return Response()


@router.delete('/admin/{admin}', response_model=Response, summary='删除管理员')
async def delete_admin(admin: str):
    if admin not in CONF.cluster.admins:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='admin not exists')
    CONF.cluster.admins.remove(admin)
    CONF.save()
    return Response()
