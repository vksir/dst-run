from fastapi import APIRouter
from dst_run.confs.confs import CONF
from dst_run.app.models.models import Ret
from dst_run.app.models.response_models import Response
from dst_run.message_queue.task_handler import TASK_QUEUE


router = APIRouter(tags=['cluster'])


@router.post('/cluster/template/{name}', summary='从模板创建存档')
async def create_cluster_by_template(name: str):
    if name not in CONF.cluster.default_templates \
            and name not in CONF.cluster.backup_clusters:
        return Response(ret=Ret.FAILED, detail='template not exists')
    TASK_QUEUE.produce(CONF.cluster.create_cluster_by_template, name, force=True)
    TASK_QUEUE.produce(CONF.load)
    return Response()


@router.post('/cluster/backup_cluster/{name}', summary='从备份存档创建存档')
async def create_cluster_by_backup_cluster(name: str):
    TASK_QUEUE.produce(CONF.cluster.create_cluster_by_backup_cluster, name)
    return Response()
