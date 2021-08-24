#!/usr/bin/python3

import os
import re
import json
import subprocess
import threading
from typing import List
from time import strftime, localtime, sleep

import log
from tools import run_cmd, get_choose

HOME = os.environ['HOME']

PROGRAM_PATH = '{}/dst_run'.format(HOME)
TEMPLATE_PATH = '{}/dst_run/cluster_template'.format(HOME)

PROGRAM_HOME_PATH = '{}/.dst_run'.format(HOME)
CFG_FILE = '{}/.dst_run/config.json'.format(HOME)
LOG_FILE = '{}/.dst_run/dst_run.log'.format(HOME)
USER_TEMPLATE_PATH = '{}/.dst_run/cluster_template'.format(HOME)

STEAMCMD_PATH = '{}/steamcmd'.format(HOME)
DST_PATH = '{}/dst'.format(HOME)
CLUSTERS_PATH = '{}/.klei/DoNotStarveTogether'.format(HOME)
CLUSTERS_BACKUP_PATH = '{}/.klei/DoNotStarveTogether/backup'.format(HOME)


class Server:
    def __init__(self):
        self._cfg = self._read_cfg()

    def __run(self):
        while True:
            self._cfg = self._read_cfg()
            self._set_mod_setup()
            self._set_token()
            self._set_cluster_setting()

            cluster = self._get_cluster()
            if self._cfg['enable_64-bit']:
                dst_file = '{}/bin64/dontstarve_dedicated_server_nullrenderer_x64'.format(DST_PATH)
            else:
                dst_file = '{}/bin/dontstarve_dedicated_server_nullrenderer'.format(DST_PATH)
            cmd = '{} -console -cluster {}'.format(dst_file, cluster)
            log.info(f'start dst, cluster={cluster}')
            if self._cfg['enable_caves']:
                proc = run_cmd('{} -shard Master'.format(cmd),
                               '{} -shard Caves'.format(cmd), cwd='{}/bin64'.format(DST_PATH), block=False)
            else:
                proc = run_cmd('{} -shard Master'.format(cmd), cwd='{}/bin64'.format(DST_PATH), block=False)

            def tail(p, tag):
                count = 0
                while p.poll() is None:
                    out = p.stdout.readline()
                    if not out:
                        count += 1
                        if count > 10:
                            log.error(f'no out for too many times, count={count}')
                            exit(1)
                    print(f'{tag}:\t{out}', end='')
            for i in range(len(proc)):
                threading.Thread(target=tail,
                                 args=(proc[i], 'Master' if i == 0 else 'Caves'),
                                 daemon=True).start()

            while True:
                if [p.poll() for p in proc] != [None] * len(proc):
                    log.error('server exits, try to start again')
                    break
                if localtime().tm_hour == 3:
                    log.info('update server')
                    for p in proc:
                        p.send_signal(2)
                    for p in proc:
                        p.wait()
                    self.server_update()
                    log.info('update server completely, start again')
                    break
                sleep(60)

    def server_update(self):
        if not self._cfg['enable_dev']:
            run_cmd('{}/steamcmd.sh +force_install_dir {} +login anonymous '
                    '+app_update 343050 validate +quit'.format(STEAMCMD_PATH, DST_PATH))
        else:
            pass

    def _create_cluster(self, template=None):
        cluster_path = '{}/{}'.format(CLUSTERS_PATH, self._cfg['cluster'])
        if os.path.exists(cluster_path):
            run_cmd('rm -rf {}'.format(cluster_path))

        template_lst = os.listdir(TEMPLATE_PATH)
        template_lst.remove('default')
        template_lst.remove('reforged')
        template_lst = ['default', 'reforged'] + template_lst
        user_template_lst = os.listdir(USER_TEMPLATE_PATH)

        log.debug(f'template_lst={template_lst}, user_template_lst={user_template_lst}')

        if template:
            user_in = template_lst.index(template)
        else:
            user_in = get_choose({
                'title': 'Cluster Template:',
                'blocks': [
                    {
                        'title': 'Default',
                        'chooses': template_lst
                    },
                    {
                        'title': 'User',
                        'chooses': user_template_lst
                    }
                ]
            })
            if user_in in [-1, 0]:
                user_in = 1
            user_in -= 1

        if user_in < len(template_lst):
            run_cmd('cp -rf {}/{} {}'.format(TEMPLATE_PATH, template_lst[user_in], cluster_path))
        else:
            run_cmd('cp -rf {}/{} {}'.format(USER_TEMPLATE_PATH, user_template_lst[user_in - len(template_lst)],
                                             cluster_path))

    def __backup_cluster(self, cluster=None):
        if not cluster:
            cluster = self._cfg['cluster']
        if os.path.exists('{}/{}'.format(CLUSTERS_PATH, cluster)):
            file_name = strftime('{}_%Y-%m-%d_%H-%M-%S'.format(cluster), localtime())
            run_cmd('tar -czvf {}/{}.tar.gz {}'.format(CLUSTERS_BACKUP_PATH, file_name, cluster), cwd=CLUSTERS_PATH)

    def run(self):
        while True:
            self._show_info()
            user_in = get_choose({
                'title': 'What to do?',
                'blocks': [
                    {
                        'title': 'Start',
                        'chooses': ['Run', 'Update/Run', 'New Cluster']
                    },
                    {
                        'title': 'Setting',
                        'chooses': ['World Setting', 'Mods Setting']
                    },
                    {
                        'title': 'Others',
                        'chooses': ['Cluster Management', 'Exit']
                    }
                ]
            })
            if user_in in [-1, 0]:
                log.info('dst_run exit with code 0')
                exit()

            if user_in in [1, 2]:
                cluster = self._get_cluster()
                if not os.path.exists('{}/{}'.format(CLUSTERS_PATH, cluster)):
                    self._create_cluster(template='reforged' if self._cfg['enable_reforged'] else None)
                if user_in == '2':
                    self.server_update()
                self.__run()
            elif user_in == 3:
                if self._cfg['enable_reforged']:
                    print('Permission denied. For your server type is Reforged.')
                else:
                    user_in_2 = get_choose({
                        'title': 'Are you sure to generate a new cluster?'
                    })
                    if user_in_2 == 1:
                        user_in_3 = get_choose({
                            'title': 'Backup the current cluster?'
                        }, expect_no=False)
                        if user_in_3 == 2:
                            self.__backup_cluster()
                        self._create_cluster()
            elif user_in == 4:
                if self._cfg['enable_reforged']:
                    print('Permission denied. For your server type is Reforged.')
                    continue

                user_in_2 = get_choose({
                    'title': 'Which to change?',
                    'blocks': [
                        {
                            'title': 'Shard',
                            'chooses': ['Master Setting', 'Caves Setting']
                        },
                        {
                            'title': 'Others',
                            'chooses': ['Exit']
                        }
                    ]
                })
                if user_in_2 not in [1, 2]:
                    continue
                cluster = self._get_cluster()
                shard = ['Master', 'Caves'][user_in_2 - 1]
                setting_file = '{}/{}/{}/leveldataoverride.lua'.format(CLUSTERS_PATH, cluster, shard)

                chooses = self._cfg['world_setting']['chooses']
                setting_lst = [k for k in chooses]
                user_in_2 = get_choose({
                    'title': 'Which to change?',
                    'blocks': [
                        {
                            'title': '{} Setting'.format(shard),
                            'chooses': setting_lst
                        },
                        {
                            'title': 'Others',
                            'chooses': ['Exit']
                        }
                    ]
                })
                if user_in_2 in range(1, len(setting_lst) + 1):
                    setting = setting_lst[user_in_2 - 1]
                    user_in_3 = get_choose({
                        'title': 'Which to choose?',
                        'blocks': [
                            {
                                'title': setting,
                                'chooses': chooses[setting]
                            }
                        ]
                    })
                    if user_in_3 in range(1, len(chooses[setting]) + 1):
                        self._cfg['world_setting'][shard][setting] = chooses[setting][user_in_3 - 1]
                        self._save_cfg(self._cfg)


            elif user_in == 5:
                while True:
                    user_in_2 = get_choose({
                        'title': 'What to do?',
                        'blocks': [
                            {
                                'title': 'Mods Check',
                                'chooses': ['Show Mods List']
                            },
                            {
                                'title': 'Mods Increase',
                                'chooses': ['By Modoverrides', 'By Mod ID']
                            },
                            {
                                'title': 'Mods Delete',
                                'chooses': ['By Mods List', 'By Mod ID']
                            },
                            {
                                'title': 'Others',
                                'chooses': ['Edit Modoverrides File by vim',
                                            'Edit Modoverrides File by nano',
                                            'Exit']
                            }
                        ]
                    })
                    if user_in_2 == 1:
                        print('Mod List:')
                        for i, mod in enumerate(self._read_modoverrides()):
                            print('  ({}) {}'.format(i + 1, mod['id']))
                    elif user_in_2 in [2, 3]:
                        if user_in_2 == 2:
                            user_in_3 = input('Input all content in modoverrides file:')
                            mod_lst_1 = self._read_modoverrides(data=user_in_3)
                            if mod_lst_1 == -1:
                                mod_lst_1 = []
                                print('Input format is incorrect.')
                        else:
                            user_in_3 = input('Input mod id:')
                            mod_lst_1 = []
                            for mod_id in user_in_3.split():
                                mod_lst_1.append({
                                    user_in_3: '["workshop-%s"]={ configuration_options={ }, enabled=true }' % mod_id
                                })

                        mod_lst_2 = self._read_modoverrides()
                        mod_lst_2 = mod_lst_2 if mod_lst_2 != -1 else []
                        self._save_modoverrides(mod_lst_1 + mod_lst_2)

                    elif user_in_2 == 4:
                        user_in_3 = get_choose({
                            'title': 'Which mod to delete?',
                            'blocks': [
                                {
                                    'title': 'Mod List',
                                    'chooses': [i for i in self._read_modoverrides()]
                                },
                                {
                                    'title': 'Others',
                                    'choose': ['Exit']
                                }
                            ]
                        })

                    elif user_in_2 == 5:
                        user_in_3 = input('Input mod id which you want to delete:')

                    elif user_in_2 in [6, 7]:
                        editor = 'vim' if user_in_2 == 6 else 'nano'
                        cluster = self._get_cluster()
                        run_cmd('{} {}/{}/Master/modoverrides.lua'.format(editor, CLUSTERS_PATH, cluster))

                    else:
                        break

            elif user_in == 6:
                self._show_info()
                user_in_2 = get_choose({
                    'title': 'What to do?',
                    'blocks': [
                        {
                            'title': 'Change Server Type',
                            'chooses': ['Master & Caves', 'Only Master', 'Reforged']
                        },
                        {
                            'title': 'Change Cluster',
                            'chooses': ['Cluster_{}'.format(i) for i in range(1, 4)]
                        }
                    ]
                })
                if user_in_2 in [-1, 0]:
                    print('Do nothing.')
                    continue

                if user_in_2 in [1, 2, 3]:
                    self._cfg['enable_reforged'] = True if user_in_2 == 3 else False
                    self._cfg['enable_caves'] = True if user_in_2 == 1 else False
                elif user_in_2 in [4, 5, 6]:
                    self._cfg['cluster'] = 'Cluster_{}'.format(user_in_2 - 3)

                self._save_cfg(self._cfg)

                cluster = self._get_cluster()
                if not os.path.exists(f'{CLUSTERS_PATH}/{cluster}'):
                    print(f'There is no {cluster} World. You should create one now.')
                    self._create_cluster()

    def _show_info(self):
        # run_cmd('clear')
        print(
            '==================== DST_Run ====================\n'
            'Room Name:\t\t\t\t{1[cluster_name][name]}\n'
            'Password:\t\t\t\t{1[cluster_password]}\n'
            'Directly connection:\tc_connect(\"{0[ip]}\", 10999)\n'
            '\n'
            'Cluster Name:\t\t\t{0[cluster]}\n'
            'Server Version:\t\t\t{0[version]}\n'
            '============= By Villkiss (Ver 1.1.0)=============\n'.format(
                self._cfg, self._cfg['room_setting'])
        )

    def _init_cfg(self) -> dict:
        cluster_token = input('No cluster_token found.\n'
                              'Please input your cluster_token: ')
        default = 'default'
        ip = self._get_ip()
        version = self._get_version()
        cfg = {
            'cluster': 'Cluster_1',
            'enable_reforged': False,
            'enable_caves': True,
            'enable_64-bit': True,
            'enable_dev': False,
            'cluster_token': cluster_token,
            'ip': ip,
            'version': version,
            'room_setting': {
                'cluster_name': {
                    'name': 'DST Run',
                    'name_surround': '󰀅'
                },
                'cluster_password': '6666',
                'tick_rate': '15'
            },
            'adminlist': [],
            'world_setting': {
                'Master': {
                    'world_size': default,
                    'specialevent': default
                },
                'Caves': {
                    'world_size': default,
                    'specialevent': default
                },
                'chooses': {
                    'world_size': ['small', 'medium', 'default', 'huge'],
                    'specialevent': ['default', 'crow_carnival', "hallowed_nights",
                                     "winters_feast", "year_of_the_gobbler", "year_of_the_varg",
                                     "year_of_the_pig", "year_of_the_carrat", "year_of_the_beefalo"]
                }
            }
        }
        self._save_cfg(cfg)
        return cfg

    def _get_ip(self):
        return ''

    def _get_version(self) -> str:
        try:
            with open('{}/version.txt'.format(DST_PATH), 'r') as f:
                version = f.read().strip()
        except Exception as e:
            log.error('get version: {}'.format(e))
            version = ''
        return version

    def _get_cluster(self) -> str:
        return 'reforged' if self._cfg['enable_reforged'] else self._cfg['cluster']

    def _read_cfg(self) -> dict:
        try:
            with open(CFG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            log.error('read cfg: {}'.format(e))
            return self._init_cfg()

    def _save_cfg(self, cfg: dict):
        with open(CFG_FILE, 'w') as f:
            json.dump(cfg, f)

    def _read_modoverrides(self, data=None):
        cluster = self._get_cluster()
        modoverrides_path = '{}/{}/Master/modoverrides.lua'.format(CLUSTERS_PATH, cluster)

        mod_lst = []
        if not data:
            if not os.path.exists(modoverrides_path):
                return mod_lst
            with open(modoverrides_path, 'r') as f:
                data = f.read()
        try:
            id_lst = re.findall(r'(?<="workshop-).*?(?=")', data)
            option_lst = re.findall(r'\[.*?enabled.*?\}', data, re.S)
            for i in range(len(id_lst)):
                mod_lst.append({
                    'id': id_lst[i],
                    'option': option_lst[i]
                })
            return mod_lst
        except Exception as e:
            msg = 'read modoverrides: {}'.format(e)
            print(msg)
            log.error(msg)
            return -1

    def _save_modoverrides(self, mod_lst: List[dict]):
        cluster = self._get_cluster()
        with open('{}/{}/Master/modoverrides.lua'.format(CLUSTERS_PATH, cluster), 'w') as f:
            f.write('return {\n')
            for i, mod in enumerate(mod_lst):
                f.write('  {},\n'.format(mod) if i + 1 == len(mod_lst)
                        else '  {}\n'.format(mod))
            f.write('}\n')

    def _set_mod_setup(self):
        cluster = self._get_cluster()

        master_modoverrides_file = '{}/{}/Master/modoverrides.lua'.format(CLUSTERS_PATH, cluster)
        caves_modoverrides_file = '{}/{}/Caves/modoverrides.lua'.format(CLUSTERS_PATH, cluster)
        mod_setup_file = '{}/mods/dedicated_server_mods_setup.lua'.format(DST_PATH)

        with open(mod_setup_file, 'w') as f:
            for i in self._read_modoverrides():
                f.write('ServerModSetup("' + i['id'] + '")\n')

        if self._cfg['enable_caves']:
            run_cmd('cp -f %s %s' % (master_modoverrides_file, caves_modoverrides_file))

    def _set_token(self):
        with open('{}/{}/cluster_token.txt'.format(CLUSTERS_PATH, self._cfg['cluster']), 'w') as f:
            f.write(self._cfg['cluster_token'])

    def _set_cluster_setting(self):
        pass


if __name__ == '__main__':
    path_lst = dir()
    for path in path_lst:
        if path.isupper() and path.endswith('PATH') and not os.path.exists(eval(path)):
            run_cmd('mkdir -p {}'.format(eval(path)))
    log.init()
    dst_server = Server()
    dst_server.run()
