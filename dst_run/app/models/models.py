import enum
from enum import Enum
from pydantic import BaseModel


class Action(Enum):
    START = 'start'
    STOP = 'stop'
    RESTART = 'restart'
    UPDATE = 'update'
    REGENERATE = 'regenerate'


class GameMode(Enum):
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


class Ret(Enum):
    SUCCEED = 0
    FAILED = 1


class Mod(BaseModel):
    id: str = None
    config: str = None
    name: str = None
    remark: str = None
    version: str = None
    enable: bool = None


class Status(enum.Enum):
    INACTIVE = 'INACTIVE'
    ACTIVE = 'ACTIVE'

    STARTING = 'STARTING'
    STOPPING = 'STOPPING'

    UPDATING = 'UPDATING'
    RESTARTING = 'RESTARTING'
    REGENERATING = 'REGENERATING'



