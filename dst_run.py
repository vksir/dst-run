#!/usr/bin/python3

import os
import re
import json
import subprocess
from time import strftime, localtime

HOME = os.environ['HOME']

PROGRAM_PATH = '{}/dst_run'.format(HOME)
TEMPLATE_PATH = '{}/dst_run/cluster_template'.format(HOME)

PROGRAM_HOME_PATH = '{}/.dst_run'.format(HOME)
CFG_FILE = '{}/.dst_run/config.json'.format(HOME)
LOG_FILE = '{}/.dst_run/dst_run.log'.format(HOME)

STEAMCMD_PATH = '{}/steamcmd'.format(HOME)
DST_PATH = '{}/dst'.format(HOME)
CLUSTERS_PATH = '{}/.klei/DoNotStarveTogether'.format(HOME)
CLUSTERS_BACKUP_PATH = '{}/.klei/DoNotStarveTogether/backup'.format(HOME)


class Server:
    def __init__(self):
        pass

    def __run(self):
        cfg = self.__read_cfg()
        cluster = 'reforged' if cfg['enable_reforged'] else cfg['cluster']

        cmd = '{}/bin/dontstarve_dedicated_server_nullrenderer -console -cluster {}'.format(DST_PATH, cluster)
        self.__set_mod_setup()
        if cfg['enable_caves']:
            run_cmd('{0} -shard Caves | sed "s/^/Caves:  /" & '
                    '{0} -shard Master | sed "s/^/Master:  /"'.format(cmd), cwd='%s/bin' % DST_PATH)
        else:
            run_cmd('{} -shard Master | sed "s/^/Master:  /"'.format(cmd), cwd='{}/bin'.format(DST_PATH))

    def __server_update(self, is_dev=False):
        if not is_dev:
            run_cmd('{}/steamcmd.sh '
                    '+force_install_dir {} '
                    '+login anonymous '
                    '+app_update 343050 '
                    'validate '
                    '+quit'.format(STEAMCMD_PATH, DST_PATH))
        else:
            pass

    def __create_cluster(self, template='default'):
        # TODO
        cfg = self.__read_cfg()
        cluster = cfg['cluster']
        cluster_path = '{}/{}'.format(CLUSTERS_PATH, cluster)
        if os.path.exists(cluster_path):
            run_cmd('rm -rf {}'.format(cluster_path))
        run_cmd('cp -rf {}/{} {}'.format(TEMPLATE_PATH, template, cluster_path))
        with open('{}/{}/cluster_token.txt'.format(CLUSTERS_PATH, cluster), 'w', encoding='utf-8') as f:
            f.write(cfg['cluster_token'])

    def __backup_cluster(self, cluster: str):
        if os.path.exists('{}/{}'.format(CLUSTERS_PATH, cluster)):
            file_name = strftime('{}_%Y-%m-%d-%H-%M-%S'.format(cluster), localtime())
            run_cmd('tar -czvf {}/{}.tar.gz {}'.format(CLUSTERS_BACKUP_PATH, file_name, cluster), cwd=CLUSTERS_PATH)

    def run(self):
        while True:
            cfg = self.__read_cfg()
            self.__show_info(cfg)
            print(
                'What to do?\n'
                '------ Start ------\n'
                '  (1) Run\n'
                '  (2) Update/Run\n'
                '  (3) New Cluster\n'
                '------ Setting ------\n'
                '  (4) World Setting\n'
                '  (5) Mods Setting\n'
                '------ Others ------\n'
                '  (6) Cluster Management\n'
                '  (7) Reinstall\n'
                '  (8) Exit\n'
            )
            user_in = input()

            if user_in == '1' or user_in == '2':
                if not os.path.exists('{}/{}'.format(CLUSTERS_PATH, cfg['cluster'])):
                    if cfg['enable_reforged']:
                        self.__create_cluster(template='reforged')
                    else:
                        self.__create_cluster()

                if user_in == '2':
                    self.__server_update()
                self.__run()
            elif user_in == '3':
                if cfg['enable_reforged']:
                    print('Permission denied, for your server type is Reforged.')
                else:
                    user_in_2 = input('Are you sure to generate a new cluster? (y/n)')
                    if user_in_2 == 'y':
                        user_in_3 = input('Backup the current cluster? (y/n)')
                        if not user_in_3 == 'n':
                            self.__backup_cluster(cfg['cluster'])
                        self.__create_cluster()
            elif user_in == '4':
                # TODO
                pass
            elif user_in == '5':
                # TODO
                pass
            elif user_in == '6':
                self.__show_info(cfg)
                print(
                    'What to do? (Print "e" to exit.)\n'
                    '----------- Choose Server Type -----------\n'
                    '  (1) Master & Caves\n'
                    '  (2) Only Master\n'
                    '  (3) Reforged\n'
                    '------------ Choose Cluster ------------\n'
                    '  (4) Cluster_1\n'
                    '  (5) Cluster_2\n'
                    '  (6) Cluster_3'
                )
                user_in_2 = input()
                if user_in_2 == '1':
                    cfg['enable_reforged'] = False
                    cfg['enable_caves'] = True
                elif user_in_2 == '2':
                    cfg['enable_reforged'] = False
                    cfg['enable_caves'] = False
                elif user_in_2 == '3':
                    cfg['enable_reforged'] = True
                    cfg['enable_caves'] = False
                elif user_in_2 == '4':
                    cfg['cluster'] = 'Cluster_1'
                elif user_in_2 == '5':
                    cfg['cluster'] = 'Cluster_2'
                elif user_in_2 == '6':
                    cfg['cluster'] = 'Cluster_3'
                self.__save_cfg(cfg)
            elif user_in == '7':
                # TODO
                try:
                    run_cmd('apt install libstdc++6:i386 libgcc1:i386 libcurl4-gnutls-dev:i386 -y',
                            'mkdir -p %s' % STEAMCMD_PATH,
                            'wget "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz"',
                            'tar -xzvf steamcmd_linux.tar.gz',
                            'rm steamcmd_linux.tar.gz', cwd=STEAMCMD_PATH, sudo=True)
                    self.__server_update()
                except Exception as e:
                    log(str(e))
                    print(e)
                    exit(1)
            elif user_in == '8':
                exit()
            else:
                pass

    def __show_info(self, cfg: dict):
        # TODO

        cluster = cfg['cluster']
        # version = cfg['version']

        # run_cmd('clear')
        print(
            '==================== DST_Run ====================\n'
            'Room Name:\t\t\t\t{}\n'
            'Password:\t\t\t\t{}\n'
            'Directly connection:\t{}\n'
            '\n'
            'Cluster Name:\t\t\t{}\n'
            'Server Version:\t\t\t{}\n'
            '============= By Villkiss (Ver 1.1.0)=============\n'.format('Name', '6666', 'Code',
                                                                          cluster, '66666')
        )

    def __init_cfg(self) -> dict:
        cluster_token = input('No cluster_token found.\nPlease input your cluster_token: ')
        cfg = {
            'cluster': 'Cluster_1',
            'enable_reforged': False,
            'enable_caves': True,
            'cluster_token': cluster_token,
            'world_setting': {

            }
        }
        self.__save_cfg(cfg)
        return cfg

    def __read_cfg(self) -> dict:
        try:
            with open(CFG_FILE, 'r', encoding='utf-8') as f:
                data = f.read()
            return json.loads(data)
        except Exception as e:
            log(str(e))
            return self.__init_cfg()

    def __save_cfg(self, cfg: dict):
        with open(CFG_FILE, 'w', encoding='utf-8') as f:
            f.write(json.dumps(cfg))

    def __set_mod_setup(self):
        cfg = self.__read_cfg()
        cluster = 'reforged' if cfg['enable_reforged'] else cfg['cluster']

        master_modoverrides_file = '{}/{}/Master/modoverrides.lua'.format(CLUSTERS_PATH, cluster)
        caves_modoverrides_file = '{}/{}/Caves/modoverrides.lua'.format(CLUSTERS_PATH, cluster)
        mod_setup_file = '{}/mods/dedicated_server_mods_setup.lua'.format(DST_PATH)

        # 生成 mod 安装文件
        with open(master_modoverrides_file, 'r', encoding='utf-8') as f:
            data = f.read()
        mod = re.findall(r'(?<="workshop-).*?(?=")', data)

        with open(mod_setup_file, 'w') as f:
            for i in mod:
                f.write('ServerModSetup("' + i + '")\n')

        # 保证 Master 和 Caves 的 mod 文件一致
        if cfg['enable_caves']:
            run_cmd('cp -f %s %s' % (master_modoverrides_file, caves_modoverrides_file))


def run_cmd(*cmd: str, cwd=None, sudo=False):
    for i in cmd:
        if sudo:
            i += 'sudo '
        proc = subprocess.run(i, shell=True, cwd=cwd, stderr=subprocess.PIPE, encoding='utf-8')
        if proc.stderr:
            log(proc.stderr)


def log(s: str):
    with open(LOG_FILE, 'w+', encoding='utf-8') as f:
        f.write(strftime('[%Y-%m-%d-%H-%M-%S] {}\n'.format(s), localtime()))



# elif user_in == '3':   # Add Mods
#     clear
#     echo "Which kind of mods to add?"
#     echo "  (1) Modoverrides"
#     echo "  (2) Mod ID"
#     echo "  (3) Exit"
#     read chose
#     if [ $chose == "1" ]
#     then
#         echo "Print Modoverrides:"
#         python3 ./mod_add.py "${cluster_dir}/${cluster}/Master/modoverrides.lua" "modoverrides"
#         set_mod
#         echo "Add success."
#     elif [ $chose == "2" ]
#     then
#         echo "Print Mod ID:"
#         python3 ./mod_add.py "${cluster_dir}/${cluster}/Master/modoverrides.lua" "modid"
#         set_mod
#         echo "Add success."
#     elif [ $chose == "3" ]     # Exit
#     then
#         echo "Exit."
#     else
#         echo "Command Error."
#     fi


if __name__ == '__main__':
    path = [
        CLUSTERS_PATH,
        CLUSTERS_BACKUP_PATH,
        PROGRAM_HOME_PATH
    ]
    for i in path:
        if not os.path.exists(i):
            run_cmd('mkdir -p {}'.format(i))

    dst_server = Server()
    dst_server.run()
