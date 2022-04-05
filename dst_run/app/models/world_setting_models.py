from enum import Enum
from pydantic import BaseModel, Field


class Frequency(str, Enum):
    never = 'never'
    rare = 'rare'
    default = 'default'
    often = 'often'
    always = 'always'


class Rate(str, Enum):
    never = 'never'
    very_slow = 'veryslow'
    slow = 'slow'
    default = 'default'
    fast = 'fast'
    very_fast = 'veryfast'


class Rarity(str, Enum):
    never = 'never'
    rare = 'rare'
    uncommon = 'uncommon'
    default = 'default'
    often = 'often'
    mostly = 'mostly'
    always = 'always'
    insane = 'insane'


class SpecialEvent(str, Enum):
    none = 'none'
    default = 'default'
    crow_carnival = 'crow_carnival'
    hallowed_nights = 'hallowed_nights'
    winters_feast = 'winters_feast'
    year_of_the_gobbler = 'year_of_the_gobbler'
    year_of_the_varg = 'year_of_the_varg'
    year_of_the_pig = 'year_of_the_pig'
    year_of_the_carrat = 'year_of_the_carrat'
    year_of_the_beefalo = 'year_of_the_beefalo'


class SpecialEventEnable(str, Enum):
    default = 'default'
    enabled = 'enabled'


class TaskSet(str, Enum):
    classic = 'classic'
    default = 'default'
    cave_default = 'cave_default'


class WorldSize(str, Enum):
    small = 'small'
    medium = 'medium'
    default = 'default'
    huge = 'huge'


class PrefabSwapsStart(str, Enum):
    classic = 'classic'
    default = 'default'
    highly_random = 'highly random'


class BaseWorld(BaseModel):
    # 世界选项-活动
    specialevent: SpecialEvent = Field(None, title='活动')

    crow_carnival: SpecialEventEnable = Field(None, title='盛夏鸦年华')
    hallowed_nights: SpecialEventEnable = Field(None, title='万圣夜')
    winters_feast: SpecialEventEnable = Field(None, title='冬季盛宴')
    year_of_the_varg: SpecialEventEnable = Field(None, title='火鸡之年')
    year_of_the_gobbler: SpecialEventEnable = Field(None, title='座狼之年')
    year_of_the_pig: SpecialEventEnable = Field(None, title='猪王之年')
    year_of_the_carrat: SpecialEventEnable = Field(None, title='胡萝卜鼠之年')
    year_of_the_beefalo: SpecialEventEnable = Field(None, title='皮弗娄牛之年')
    year_of_the_catcoon: SpecialEventEnable = Field(None, title='浣猫之年')

    # 世界选项-世界
    weather: Frequency = Field(None, title='雨')

    # 世界选项-资源再生
    regrowth: Rate = Field(None, title='重生速度')

    # 世界选项-巨兽
    fruitfly: Frequency = Field(None, title='果蝇王')
    liefs: Frequency = Field(None, title='树精守卫')
    spiderqueen: Frequency = Field(None, title='蜘蛛女王')

    # 世界生成-世界
    world_size: WorldSize = Field(None, title='世界大小')
    prefabswaps_start: PrefabSwapsStart = Field(None, title='开始资源多样化')


class Master(BaseWorld):
    # 世界选项-世界
    hunt: Frequency = Field(None, title='狩猎')
    wildfires: Frequency = Field(None, title='野火')
    lightning: Frequency = Field(None, title='闪电')
    frograin: Frequency = Field(None, title='青蛙雨')
    petrification: Frequency = Field(None, title='森林石化')
    meteorshowers: Frequency = Field(None, title='流星频率')
    hounds: Frequency = Field(None, title='猎犬袭击')
    alternatehunt: Frequency = Field(None, title='追猎惊喜')

    # 世界选项-敌对生物
    walrus_setting: Frequency = Field(None, title='海象')
    cookiecutters: Frequency = Field(None, title='饼干切割机')

    # 世界选项-巨兽
    bearger: Frequency = Field(None, title='熊獾')
    beequeen: Frequency = Field(None, title='蜂王')
    dragonfly: Frequency = Field(None, title='龙蝇')
    klaus: Frequency = Field(None, title='克劳斯')
    crabking: Frequency = Field(None, title='帝王蟹')
    malbatross: Frequency = Field(None, title='邪天翁')
    goosemoose: Frequency = Field(None, title='麋鹿鹅')
    deciduousmonster: Frequency = Field(None, title='毒桦栗树')
    deerclops: Frequency = Field(None, title='独眼巨鹿')
    antliontribute: Frequency = Field(None, title='蚁狮贡品')
    eyeofterror: Frequency = Field(None, title='恐怖之眼')

    # 世界生成-敌对生物刷新点
    walrus: Rarity = Field(None, title='海象营地')


class Caves(BaseWorld):
    # 世界选项-世界
    earthquakes: Frequency = Field(None, title='地震')
    atriumgate: Frequency = Field(None, title='远古大门')
    wormattacks: Frequency = Field(None, title='洞穴蠕虫攻击')

    # 世界选项-巨兽
    toadstool: Frequency = Field(None, title='毒菌蟾蜍')
