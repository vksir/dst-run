from fastapi import APIRouter
from dst_run.confs.confs import CONF
from dst_run.app.models.response_models import Response


router = APIRouter(tags=['admin'])


@router.get('/admin', response_model=Response, summary='获取管理员')
async def get_admins():
    return Response(admins=CONF.cluster.admins)


@router.post('/admin/{admin}', response_model=Response, summary='添加管理员')
async def get_admins(admin: str):
    CONF.cluster.admins.append(admin)
    return Response()


@router.delete('/admin/{admin}', response_model=Response, summary='删除管理员')
async def get_admins(admin: str):
    CONF.cluster.admins.pop(admin, None)
    return Response()
