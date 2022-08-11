from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status
from dst_run.confs.confs import CONF
from dst_run.app.models.models import Status
from dst_run.app.models.response_models import Response
from dst_run.agent.controller import CONTROLLER


router = APIRouter(tags=['cluster'])


@router.post('/cluster/template/{name}', response_model=Response, summary='从模板创建存档')
async def create_cluster_by_template(name: str):
    if name not in CONF.cluster.default_templates \
            and name not in CONF.cluster.custom_templates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='template not exists')

    if CONTROLLER.status != Status.INACTIVE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'server is {CONTROLLER.status_str}, could not operate cluster')

    CONF.cluster.create_cluster_by_template(name, force=True)
    CONF.load()
    return Response()


@router.post('/cluster/backup_cluster/{name}', response_model=Response, summary='从备份存档创建存档')
async def create_cluster_by_backup_cluster(name: str):
    if CONTROLLER.status != Status.INACTIVE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'server is {CONTROLLER.status_str}, could not operate cluster')
    CONF.cluster.create_cluster_by_backup_cluster(name)
    return Response()
