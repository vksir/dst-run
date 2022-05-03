from fastapi import APIRouter
from dst_run.confs.confs import CONF
from dst_run.app.models.response_models import Response
from dst_run.app.models.response_models import ResponseCluster
from dst_run.message_queue.task_handler import TASK_QUEUE


router = APIRouter(tags=['cluster template'])


@router.get('/template', response_model=Response, summary='获取模板列表')
async def list_template():
    cluster = ResponseCluster(default_templates=CONF.cluster.default_templates,
                              custom_templates=CONF.cluster.custom_templates)
    return Response(cluster=cluster)


@router.post('/template/{name}', response_model=Response, summary='创建模板')
async def create_custom_template(name: str):
    CONF.cluster.create_custom_template_by_cluster(name)
    return Response()


@router.delete('/template/{name}', response_model=Response, summary='删除模板')
async def delete_custom_template(name: str):
    CONF.cluster.delete_custom_template(name)
    return Response()


@router.put('/template/{name}', response_model=Response, summary='重命名模板')
async def rename_custom_template(name: str, new_name: str):
    CONF.cluster.rename_custom_template(name, new_name)
    return Response()
