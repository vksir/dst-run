from fastapi import Query
from dst_run.app.app import app
from dst_run.confs.confs import CONF
from dst_run.app.models.response_models import Response
from dst_run.app.models.response_models import ResponseCluster
from dst_run.message_queue.task_handler import TASK_QUEUE


@app.get('/backup_cluster', tags=['backup cluster'], response_model=Response, summary='获取备份存档列表')
async def list_backup_cluster():
    cluster = ResponseCluster(backup_clusters=CONF.cluster.backup_clusters)
    return Response(cluster=cluster)


@app.post('/backup_cluster/{name}', tags=['backup cluster'], response_model=Response, summary='创建备份存档')
async def create_backup_cluster(name: str = None):
    TASK_QUEUE.produce(CONF.cluster.create_backup_cluster, name)
    return Response()


@app.delete('/backup_cluster/{name}', tags=['backup cluster'], response_model=Response, summary='删除备份存档')
async def delete_backup_cluster(name: str):
    TASK_QUEUE.produce(CONF.cluster.delete_backup_cluster, name)
    return Response()


@app.put('/backup_cluster/{name}', tags=['backup cluster'], response_model=Response, summary='重命名备份存档')
async def rename_backup_cluster(name: str, new_name: str = Query(..., alias='name')):
    TASK_QUEUE.produce(CONF.cluster.rename_backup_cluster, name, new_name)
    return Response()
