import re
from typing import List
from typing import Union
from dst_run.common.constants import FilePath
from dst_run.common.constants import Constants
from dst_run.common.log import log
from dst_run.confs.base_conf import BaseConf


class ModConf(BaseConf):
    def deploy(self):
        self._deploy_mod_setting()
        self._deploy_mod_setup()

    def load(self):
        with open(FilePath.MASTER_MOD_SETTING_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        for mod in self.values():
            mod['enable'] = False
        self.add_by_content(content)

    @property
    def _default(self) -> dict:
        return {}

    def _deploy_mod_setting(self):
        mod_setting = 'return {\n'
        for mod in self.values():
            mod_enable = mod['enable']
            mod_config = mod['config']
            if not mod_enable:
                continue
            mod_setting += f'  {mod_config},\n'
        mod_setting = mod_setting[:-2] + '\n}'
        with open(FilePath.MASTER_MOD_SETTING_PATH, 'w', encoding='utf-8') as f:
            f.write(mod_setting)
        with open(FilePath.CAVES_MOD_SETTING_PATH, 'w', encoding='utf-8') as f:
            f.write(mod_setting)

    def _deploy_mod_setup(self):
        mod_setup = ''
        for mod in self.values():
            mod_id = mod['id']
            mod_enable = mod['enable']
            if not mod_enable:
                continue
            mod_setup += f'ServerModSetup("{mod_id}")\n'
        with open(FilePath.MOD_SETUP_PATH, 'w', encoding='utf-8') as f:
            f.write(mod_setup)

    @property
    def mod_ids(self) -> List[str]:
        return list(self)

    @property
    def mods(self) -> List[dict]:
        return list(self.values())

    def get_mod(self, mod_id: str) -> Union[None, dict]:
        if mod_id not in self:
            return None
        return self[mod_id]

    def update_mod(self, mod_id: str, mod_data: dict) -> int:
        if mod_id not in self:
            return Constants.RET_FAILED
        self[mod_id].update(mod_data)
        return Constants.RET_SUCCEED

    def _add_mod(self, mod_id: str, mod_config: str):
        self[mod_id] = {
            'id': mod_id,
            'name': '',
            'remark': '',
            'version': '',
            'config': mod_config,
            'enable': True
        }

    def add_by_mod_id(self, mod_id: str) -> None:
        mod_config = '["workshop-%s"]={ configuration_options={ }, enabled=true }' % mod_id
        self._add_mod(mod_id, mod_config)

    def add_by_content(self, content: str) -> int:
        mod_ids = re.findall(r'\["workshop-(\d+)"\]=\{.*?\{.*?\}.*?enabled.*?\}', content, re.S)
        mod_configs = re.findall(r'\["workshop-\d+"\]=\{.*?\{.*?\}.*?enabled.*?\}', content, re.S)
        if len(mod_ids) != len(mod_configs):
            log.error(f'regex mod failed: mod_ids={mod_ids}, mod_configs={mod_configs}, content={content}')
            return Constants.RET_FAILED

        for mod_id, mod_config in zip(mod_ids, mod_configs):
            self._add_mod(mod_id, mod_config)
        return Constants.RET_SUCCEED

    def delete_mod_by_ids(self, mod_ids: List[str]) -> None:
        for mod_id in mod_ids:
            self.pop(mod_id, None)
