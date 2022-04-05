from dst_run.app.app import app
from dst_run.app.models.models import Action
from dst_run.app.models.models import Ret
from dst_run.app.models.response_models import Response
from dst_run.confs.confs import CONF
from dst_run.agent.agent import AGENT
from dst_run.message_queue.task_handler import TASK_QUEUE


def start():
    TASK_QUEUE.produce(CONF.deploy)
    TASK_QUEUE.produce(AGENT.run)


def stop():
    TASK_QUEUE.produce(AGENT.stop)


def restart():
    TASK_QUEUE.produce(AGENT.stop)
    TASK_QUEUE.produce(AGENT.start)


def update():
    TASK_QUEUE.produce(AGENT.update)


@app.post('/action/{action}', response_model=Response, summary='饥荒服务器控制')
async def action(act: Action):
    mapping = {
        act.START: start,
        act.STOP: stop,
        act.RESTART: restart,
        act.UPDATE: update
    }
    if act not in mapping:
        return Response(ret=Ret.FAILED, detail='invalid action type')
    mapping[act]()
    return Response()
