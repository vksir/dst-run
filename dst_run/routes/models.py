from enum import Enum
from pydantic import BaseModel


class Action(str, Enum):
    START = 'START'
    STOP = 'STOP'
    RESTART = 'RESTART'
    UPDATE = 'UPDATE'


class GameMode(str, Enum):
    endless: str = 'endless'
    wilderness: str = 'wilderness'
    survival: str = 'survival'


class GamePlay(BaseModel):
    game_mode: GameMode = None
    max_players: int = None
    pvp: bool = None


class Network(BaseModel):
    cluster_name: str = None
    cluster_password: str = None
    cluster_description: str = None


class Room(BaseModel):
    GAMEPLAY: GamePlay = None
    NETWORK: Network = None


class Data(BaseModel):
    data: str


class Ret(int, Enum):
    SUCCESS = 0
    FAILED = 1


class BaseResponse(BaseModel):
    ret: Ret
    detail: str = ''


class Status(str, Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'


class ServerStatus(BaseModel):
    status: Status


class Mod(BaseModel):
    id: str
    name: str = None
    remark: str = None
    version: str = None
    config: str
    enable: bool = True


class ModModify(BaseModel):
    remark: str = None
    config: str = None
    enable: bool = None


def filter_value_none(data):
    if not isinstance(data, dict):
        return data
    return {key: filter_value_none(value) for key, value in data.items() if value is not None}


def deep_update(origin: dict, new_data: dict):
    for key, value in new_data.items():
        if isinstance(value, dict) and key in origin:
            deep_update(origin[key], value)
        else:
            origin[key] = value
