from typing import List

from pydantic import BaseModel
from dst_run.routes.models.models import *
from dst_run.routes.models.world_setting_models import Master
from dst_run.routes.models.world_setting_models import Caves


class Response(BaseModel):
    ret: Ret = Ret.SUCCEED
    detail: str = ''
    room: Room = None
    master: Master = None
    caves: Caves = None
    mods: List[Mod] = None

