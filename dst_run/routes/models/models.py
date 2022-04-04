from enum import Enum
from pydantic import BaseModel


class Action(Enum):
    START = 'START'
    STOP = 'STOP'
    RESTART = 'RESTART'
    UPDATE = 'UPDATE'


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


class Data(BaseModel):
    data: str


class Ret(Enum):
    SUCCEED = 0
    FAILED = 1


class Mod(BaseModel):
    id: str
    config: str
    name: str = None
    remark: str = None
    version: str = None
    enable: bool = True




