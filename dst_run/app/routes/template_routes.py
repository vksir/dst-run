from fastapi import APIRouter
from fastapi import Depends
from dst_run.app.dependencies import verify_token
from dst_run.confs.confs import CONF
from dst_run.app.models.response_models import Response
from dst_run.app.models.response_models import ResponseCluster
from dst_run.message_queue.task_handler import TASK_QUEUE


router = APIRouter(tags=['cluster template'], 
                   dependencies=[Depends(verify_token)])


@router.get('/template', summary='获取模板列表')
async def list_template():
    cluster = ResponseCluster(default_templates=CONF.cluster.default_templates,
                              custom_templates=CONF.cluster.custom_templates)
    return Response(cluster=cluster)


@router.post('/template/{name}', summary='创建模板')
async def create_custom_template(name: str):
    TASK_QUEUE.produce(CONF.cluster.create_custom_template, name)
    return Response()


@router.delete('/template/{name}', summary='删除模板')
async def delete_custom_template(name: str):
    TASK_QUEUE.produce(CONF.cluster.delete_custom_template, name)
    return Response()


@router.put('/template/{name}', summary='重命名模板')
async def rename_custom_template(name: str, new_name: str):
    TASK_QUEUE.produce(CONF.cluster.rename_custom_template, name, new_name)
    return Response()
