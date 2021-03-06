from fastapi import APIRouter
from fastapi import Path
from dst_run.app.models.models import Action
from dst_run.app.models.response_models import Response
from dst_run.agent.controller import CONTROLLER
from dst_run.message_queue.task_handler import TASK_QUEUE


router = APIRouter()


@router.post('/action/{action}', response_model=Response, summary='饥荒服务器控制')
async def action(act: Action = Path(..., alias='action')):
    TASK_QUEUE.produce(getattr(CONTROLLER, act.value.lower()))
    return Response()
