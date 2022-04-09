from dst_run.app.app import app
from dst_run.app.models.models import Action
from dst_run.app.models.response_models import Response
from dst_run.agent.agent import AGENT
from dst_run.message_queue.task_handler import TASK_QUEUE


@app.post('/action/{action}', response_model=Response, summary='饥荒服务器控制')
async def action(act: Action):
    TASK_QUEUE.produce(getattr(AGENT, act.value.lower()))
    return Response()
