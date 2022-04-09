import os
import time
from typing import List
from dst_run.common.constants import FilePath
from dst_run.common.constants import Constants
from dst_run.common.utils import run_cmd
from dst_run.common.log import log
from dst_run.confs.base_conf import BaseConf


class ClusterConf(BaseConf):
    def deploy(self):
        self.create_cluster_by_template(force=False)
        self._deploy_admins()
        self._deploy_token()

    def load(self):
        self.create_cluster_by_template(force=False)

    def _get_init_data(self):
        token = input('Please input your token: ')
        return {
            'token': token,
            'admins': []
        }

    def _deploy_admins(self):
        admin_data = '\n'.join(self['admins'])
        with open(FilePath.ADMINS_PATH, 'w', encoding='utf-8') as f:
            f.write(admin_data)

    def _deploy_token(self):
        with open(FilePath.CLUSTER_TOKEN_PATH, 'w', encoding='utf-8') as f:
            f.write(self['token'])

    # cluster
    def create_cluster_by_template(self, template='default', force=True) -> int:
        if not force and os.path.exists(FilePath.CLUSTER_PATH):
            return Constants.RET_SUCCEED

        if template in self.default_templates:
            template_path = self._get_default_template_path(template)
        elif template in self.custom_templates:
            template_path = self._get_custom_template_path(template)
        else:
            log.error(f'template not found: template={template}')
            return Constants.RET_FAILED

        self.create_backup_cluster()
        run_cmd(f'rm -rf {FilePath.CLUSTER_PATH}')
        run_cmd(f'cp -rf {template_path} {FilePath.CLUSTER_PATH}')
        return Constants.RET_SUCCEED

    def create_cluster_by_backup_cluster(self, backup_cluster: str):
        pass

    # template
    @property
    def default_templates(self) -> List[str]:
        return os.listdir(FilePath.TEMPLATE_DIR)

    @property
    def custom_templates(self) -> List[str]:
        return os.listdir(FilePath.CUSTOM_TEMPLATE_DIR)

    def create_custom_template(self, name: str):
        pass

    def delete_custom_template(self, name: str):
        custom_template_path = self._get_custom_template_path(name)
        run_cmd(f'rm -rf {custom_template_path}')

    def rename_custom_template(self, old_name: str, new_name: str):
        old_path = self._get_custom_template_path(old_name)
        new_path = self._get_custom_template_path(new_name)
        if not os.path.exists(old_path):
            return
        run_cmd(f'mv -f {old_path} {new_path}')

    @staticmethod
    def _get_default_template_path(template: str):
        return f'{FilePath.TEMPLATE_DIR}/{template}'

    @staticmethod
    def _get_custom_template_path(template: str):
        return f'{FilePath.CUSTOM_TEMPLATE_DIR}/{template}'

    # backup_cluster
    @property
    def backup_clusters(self) -> List[str]:
        clusters = os.listdir(FilePath.CLUSTERS_BACKUP_DIR)
        clusters = [i.replace('.tar.gz', '') for i in clusters]
        return clusters

    @staticmethod
    def create_backup_cluster(name: str = None):
        if not os.path.exists(FilePath.CLUSTER_PATH):
            return
        if name is None:
            name = time.strftime(f'%Y-%m-%d_%H-%M-%S', time.localtime())
        run_cmd(f'tar -czf {FilePath.CLUSTERS_BACKUP_DIR}/{name}.tar.gz {FilePath.CLUSTER_NAME}',
                cwd=FilePath.CLUSTERS_DIR)

    def delete_backup_cluster(self, name: str):
        backup_cluster_path = self._get_backup_cluster_path(name)
        run_cmd(f'rm -rf {backup_cluster_path}')

    def rename_backup_cluster(self, old_name: str, new_name: str):
        old_path = self._get_backup_cluster_path(old_name)
        new_path = self._get_backup_cluster_path(new_name)
        if not os.path.exists(old_path):
            return
        run_cmd(f'mv -f {old_path} {new_path}')

    @staticmethod
    def _get_backup_cluster_path(backup_cluster: str):
        return f'{FilePath.CLUSTERS_BACKUP_DIR}/{backup_cluster}.tar.gz'
