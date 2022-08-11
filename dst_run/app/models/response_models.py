import enum
from typing import List

from pydantic import BaseModel
from dst_run.app.models.models import Ret
from dst_run.app.models.models import Room
from dst_run.app.models.models import Status
from dst_run.app.models.models import Mod


class ResponseCluster(BaseModel):
    default_templates: List[str] = None
    custom_templates: List[str] = None
    backup_clusters: List[str] = None


class ResponseWorld(BaseModel):
    master: str = None
    caves: str = None


class Response(BaseModel):
    ret: Ret = Ret.SUCCEED
    detail: str = ''
    status: Status = None
    admins: List[str] = None
    cluster: ResponseCluster = None
    room: Room = None
    world: ResponseWorld = None
    mods: List[Mod] = None
    players: List[str] = None
