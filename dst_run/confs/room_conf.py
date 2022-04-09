from configparser import ConfigParser
from dst_run.common.constants import FilePath
from dst_run.common.data_lib import DataLib
from dst_run.confs.base_conf import BaseConf


class RoomConf(BaseConf):
    EYE_ICON = '󰀅'

    def deploy(self):
        room_setting = ConfigParser()
        with open(FilePath.ROOM_SETTING_PATH, 'r', encoding='utf-8') as f:
            room_setting.read_file(f)
        for section_key, section in self.items():
            for key, value in section.items():
                if isinstance(value, int):
                    value = str(value)
                if key == 'cluster_name':
                    value = self.EYE_ICON + value + self.EYE_ICON
                room_setting[section_key][key] = value
        with open(FilePath.ROOM_SETTING_PATH, 'w', encoding='utf-8') as f:
            room_setting.write(f)

    def load(self):
        pass

    @property
    def _default(self) -> dict:
        return {
            'GAMEPLAY': {
                'game_mode': 'endless',
                'max_players': '6',
                'pvp': 'false'
            },
            'NETWORK': {
                'cluster_name': 'DST_RUN',
                'cluster_password': '6666',
                'cluster_description': 'Just Have Fun'
            }
        }

    @property
    def room(self) -> dict:
        return dict(self)

    def update_room(self, room_data: dict) -> None:
        DataLib.deep_update(self.data, room_data)
