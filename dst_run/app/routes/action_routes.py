from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status
from dst_run.app.models.models import Status
from dst_run.app.models.response_models import Response
from dst_run.agent.controller import CONTROLLER


router = APIRouter(tags=['action'])


@router.post('/action/status', response_model=Response, summary='服务器状态')
async def server_status():
    return Response(status=CONTROLLER.status)


@router.post('/action/start', response_model=Response, summary='服务器启动')
async def start():
    if CONTROLLER.status != Status.INACTIVE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'server is {CONTROLLER.status_str}, could not start')
    CONTROLLER.start()
    return Response()


@router.post('/action/stop', response_model=Response, summary='服务器停止')
async def stop():
    if CONTROLLER.status in [Status.RESTARTING,
                             Status.UPDATING,
                             Status.REGENERATING]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'server is {CONTROLLER.status_str}, could not stop')
    CONTROLLER.stop()
    return Response()


@router.post('/action/restart', response_model=Response, summary='服务器重启')
async def restart():
    if CONTROLLER.status in [Status.RESTARTING,
                             Status.UPDATING,
                             Status.REGENERATING]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'server is {CONTROLLER.status_str}, could not restart')
    CONTROLLER.restart()
    return Response()


@router.post('/action/update', response_model=Response, summary='服务器更新')
async def update():
    if CONTROLLER.status in [Status.RESTARTING,
                             Status.UPDATING,
                             Status.REGENERATING]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'server is {CONTROLLER.status_str}, could not update')
    CONTROLLER.update()
    return Response()


@router.post('/action/regenerate', response_model=Response, summary='服务器重新生成世界')
async def regenerate():
    if CONTROLLER.status in [Status.RESTARTING,
                             Status.UPDATING,
                             Status.REGENERATING]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'server is {CONTROLLER.status_str}, could not regenerate')
    CONTROLLER.regenerate()
    return Response()
