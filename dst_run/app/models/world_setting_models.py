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


class WorldOptions:
    class Global:
        """世界选项-全局"""

        class Base(BaseModel):
            pass

        class Master(BaseModel):
            specialevent: SpecialEvent = Field(None, title='活动')

        class Caves(BaseModel):
            pass

    class Event:
        """"世界选项-活动"""

        class Base(BaseModel):
            pass

        class Master(BaseModel):
            crow_carnival: SpecialEventEnable = Field(None, title='盛夏鸦年华')
            hallowed_nights: SpecialEventEnable = Field(None, title='万圣夜')
            winters_feast: SpecialEventEnable = Field(None, title='冬季盛宴')
            year_of_the_varg: SpecialEventEnable = Field(None, title='火鸡之年')
            year_of_the_gobbler: SpecialEventEnable = Field(None, title='座狼之年')
            year_of_the_pig: SpecialEventEnable = Field(None, title='猪王之年')
            year_of_the_carrat: SpecialEventEnable = Field(None, title='胡萝卜鼠之年')
            year_of_the_beefalo: SpecialEventEnable = Field(None, title='皮弗娄牛之年')
            year_of_the_catcoon: SpecialEventEnable = Field(None, title='浣猫之年')

        class Caves(BaseModel):
            pass

    class World:
        """世界选项-世界"""

        class Base(BaseModel):
            weather: Frequency = Field(None, title='雨')

        class Master(BaseModel):
            hounds: Frequency = Field(None, title='猎犬袭击')
            petrification: Frequency = Field(None, title='森林石化')
            meteorshowers: Frequency = Field(None, title='流星频率')
            hunt: Frequency = Field(None, title='狩猎')
            alternatehunt: Frequency = Field(None, title='追猎惊喜')
            wildfires: Frequency = Field(None, title='野火')
            lightning: Frequency = Field(None, title='闪电')
            frograin: Frequency = Field(None, title='青蛙雨')

        class Caves(BaseModel):
            earthquakes: Frequency = Field(None, title='地震')
            wormattacks: Frequency = Field(None, title='洞穴蠕虫攻击')
            atriumgate: Frequency = Field(None, title='远古大门')

    class ResourceGeneration:
        """世界选项-资源再生"""

        class Base(BaseModel):
            regrowth: Rate = Field(None, title='重生速度')

        class Master(BaseModel):
            pass

        class Caves(BaseModel):
            pass

    class HostileCreature:
        """世界选项-敌对生物"""

        class Base(BaseModel):
            pass

        class Master(BaseModel):
            walrus_setting: Frequency = Field(None, title='海象')
            cookiecutters: Frequency = Field(None, title='饼干切割机')

        class Caves(BaseModel):
            pass

    class Boss:
        """世界选项-巨兽"""

        class Base(BaseModel):
            fruitfly: Frequency = Field(None, title='果蝇王')
            liefs: Frequency = Field(None, title='树精守卫')
            spiderqueen: Frequency = Field(None, title='蜘蛛女王')

        class Master(BaseModel):
            klaus: Frequency = Field(None, title='克劳斯')
            crabking: Frequency = Field(None, title='帝王蟹')
            eyeofterror: Frequency = Field(None, title='恐怖之眼')
            deciduousmonster: Frequency = Field(None, title='毒桦栗树')
            bearger: Frequency = Field(None, title='熊獾')
            deerclops: Frequency = Field(None, title='独眼巨鹿')
            antliontribute: Frequency = Field(None, title='蚁狮贡品')
            beequeen: Frequency = Field(None, title='蜂王')
            malbatross: Frequency = Field(None, title='邪天翁')
            goosemoose: Frequency = Field(None, title='麋鹿鹅')
            dragonfly: Frequency = Field(None, title='龙蝇')

        class Caves(BaseModel):
            toadstool: Frequency = Field(None, title='毒菌蟾蜍')


class WorldGeneration:
    class World:
        """世界生成-世界"""

        class Base(BaseModel):
            world_size: WorldSize = Field(None, title='世界大小')
            prefabswaps_start: PrefabSwapsStart = Field(None, title='开始资源多样化')

        class Master(BaseModel):
            pass

        class Caves(BaseModel):
            pass

    class HostileCreatureSpawnPoint:
        """世界生成-敌对生物刷新点"""

        class Base(BaseModel):
            pass

        class Master(BaseModel):
            walrus: Rarity = Field(None, title='海象营地')

        class Caves(BaseModel):
            pass


def get_parent_classes(name: str):
    def get_multiple_classes(cls):
        return [v for k, v in cls.__dict__.items() if not k.startswith('_')]

    multiple_classes = get_multiple_classes(WorldOptions) + get_multiple_classes(WorldGeneration)
    classes = [getattr(multiple_class, name) for multiple_class in multiple_classes] \
        + [getattr(multiple_class, 'Base') for multiple_class in multiple_classes]
    return classes


class Master(*get_parent_classes('Master')):
    pass


class Caves(*get_parent_classes('Caves')):
    pass


if __name__ == '__main__':
    print(Master().dict())
    # import json
    #
    # data = Master.__dict__
    # data = data['__fields__']
    #
    #
    # def switch(class_name):
    #     first = class_name[0]
    #     class_name = list(class_name)
    #     class_name[0] = first.lower()
    #     return ''.join(class_name)
    #
    #
    # data = [{
    #     'title': v.field_info.title,
    #     'keyword': v.alias,
    #     'options': switch(data['specialevent'].type_.__name__)
    # } for k, v in data.items()]
    # for i in data:
    #     line = json.dumps(i, ensure_ascii=False)
    #     line = line.replace('"options": "', '"options": ')
    #     line = line.replace('"}', '}')
    #     print(line)
