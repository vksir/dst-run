#!/usr/bin/python3

import os
import re
import json
from time import strftime, localtime
from icecream import ic

HOME = os.environ['HOME']

STEAMCMD = '%s/steamcmd' % HOME
DST_DIR = '%s/dst' % HOME
DST_SERVER = '%s/bin/dontstarve_dedicated_server_nullrenderer' % DST_DIR
CLUSTER_DIR = '%s/.klei/DoNotStarveTogether' % HOME
CLUSTER_BACKUP_DIR = '%s/.klei/DoNotStarveTogether/backup' % HOME
CLUSTER_NAME = 'MyDediServer'


def update_mod_cfg(dst_dir, cluster_dir, cluster_name):
    cluster_path = '%s/%s' % (cluster_dir, cluster_name)
    master_mod_overrides_path = '%s/Master/modoverrides.lua' % cluster_path
    caves_mod_overrides_path = '%s/Caves/modoverrides.lua' % cluster_path
    mod_cfg_path = '%s/mods/dedicated_server_mods_setup.lua' % dst_dir

    # 生成 mod 安装文件
    with open(master_mod_overrides_path, 'r', encoding='utf-8') as f:
        data = f.read()
    mod = re.findall(r'(?<="workshop-).*?(?=")', data)

    with open(mod_cfg_path, 'w') as f:
        for i in mod:
            f.write('ServerModSetup("' + i + '")\n')

    # 保证 Master 和 Cave 的 mod 文件一致
    os.system('cp %s %s' % (master_mod_overrides_path, caves_mod_overrides_path))


def run_cmd(*cmd: str, cwd=None, sudo=False):
    tmp = os.getcwd()
    if cwd:
        os.chdir(cwd)

    for i in cmd:
        if sudo:
            i += 'sudo '
        os.system(i)

    os.chdir(tmp)


class Server:
    def __init__(self):
        self.__home = '%s/.dst_run' % HOME
        if not os.path.exists(self.__home):
            run_cmd('mkdir -p %s' % self.__home)
        self.__cfg_file = '%s/config.json' % self.__home

        self.__log_file = '%s/dst_run.log' % self.__home
        run_cmd('rm %s' % self.__log_file)

        self.cfg = self.__read_cfg()

    def __run(self):
        self.cfg = self.__read_cfg()
        cluster = self.cfg['cluster']

        update_mod_cfg(DST_DIR, CLUSTER_DIR, cluster)
        cmd = '%s -console -cluster %s' % (DST_SERVER, cluster)
        run_cmd(
            r'%s -shard Caves | sed "s/^/Caves:  /" & '
            r'%s -shard Master | sed "s/^/Master:  /"' % (cmd, cmd), cwd='%s/bin' % DST_DIR
        )

    def __server_update(self):
        run_cmd('%s '
                '+force_install_dir %s '
                '+login anonymous '
                '+app_update 343050 '
                'validate '
                '+quit' % ('%s/steamcmd.sh' % STEAMCMD, DST_SERVER))


    def run(self):
        self.show_info()
        print(
            'What to do?\n'
            '------ Start ------\n'
            '  (1) Run\n'
            '  (2) Update/Run\n'
            '  (3) New Cluster\n'
            '------ Setting ------\n'
            '  (4) World Setting\n'
            '  (5) Mods Setting\n'
            '------ Others ------'
            '  (6) Cluster Management\n'
            '  (7) Reinstall\n'
            '  (8) Exit\n'
        )
        user_in = input()

        if user_in == '1':
            self.__run()
        elif user_in == '2':
            self.__server_update()
            self.__run()
        elif user_in == '3':
            if self.cfg['enable_reforged']:
                print('Permission denied, for your server type is Reforged.')
            else:
                user_in_2 = input('Are you sure to generate a new cluster? (y/n)')
                if user_in_2 == 'y':
                    user_in_3 = input('Backup the current cluster? (y/n)')
                    cluster = self.cfg['cluster']
                    cluster_path = '%s/%s' % (CLUSTER_DIR, cluster)
                    if not user_in_3 == 'n':
                        self.__backup(cluster)
                    if os.path.exists(cluster_path):
                        run_cmd('rm -rf %s/*' % cluster_path)
                    else:
                        run_cmd('mkdir -p %s' % cluster_path)



        elif user_in == '6':
            self.show_info()
            print(
                'What to do? (Print "e" to exit.)\n'
                '----------- Choose Server Type -----------\n'
                '  (1) Master & Caves\n'
                '  (2) Only Master\n'
                '  (3) Reforged\n'
                '------------ Choose Cluster ------------\n'
                '  (4) MyDediServer\n'
                '  (5) MyDediServer2\n'
                '  (6) MyDediServer3'
            )
            user_in_2 = input()
            if user_in_2 == '1':
                self.cfg['enable_reforged'] = False
                self.cfg['enable_caves'] = True
            elif user_in_2 == '2':
                self.cfg['enable_reforged'] = False
                self.cfg['enable_caves'] = False
            elif user_in_2 == '3':
                self.cfg['enable_reforged'] = True
            elif user_in_2 == '4':
                self.cfg['cluster'] = 'MyDediServer'
            elif user_in_2 == '5':
                self.cfg['cluster'] = 'MyDediServer2'
            elif user_in_2 == '6':
                self.cfg['cluster'] = 'MyDediServer3'
        elif user_in == '4':
            pass
        elif user_in == '5':
            try:

                run_cmd('apt install libstdc++6:i386 libgcc1:i386 libcurl4-gnutls-dev:i386 -y',
                        'mkdir -p %s' % STEAMCMD,
                        'wget "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz"',
                        'tar -xzvf steamcmd_linux.tar.gz',
                        'rm steamcmd_linux.tar.gz', cwd=STEAMCMD, sudo=True)
                self.__server_update()
            except Exception as e:
                self.__log(str(e))
                print(e)
                exit(1)

    def show_info(self):
        # version = self.cfg['version']
        cluster = self.cfg['cluster']

        # run_cmd('clear')
        print(
            '==================== DST_Run ====================\n'
            'Room Name:\t\t\t\t%s\n'
            'Password:\t\t\t\t%s\n'
            'Directly connection:\t%s\n'
            '\n'
            'Cluster Name:\t\t\t%s\n'
            'Server Version:\t\t\t%s\n'
            '============= By Villkiss (Ver 1.1.0)============='
            % ('Name', '6666', 'Code', cluster, '66666')
        )

    def __init_cfg(self) -> dict:
        cluster_token = input('Please input your cluster_token:')
        cfg = {
            'cluster': 'MyDediServer',
            'enable_reforged': False,
            'enable_caves': True,
            'cluster_token': cluster_token,
            'world_setting': {

            },
            'default_mod_setting': {
                'Global Position':
            },

            'mod_setting': {}
        }
        self.__save_cfg(cfg)
        return cfg

    def __read_cfg(self) -> dict:
        try:
            with open(self.__cfg_file, 'r', encoding='utf-8') as f:
                data = f.read()
            return json.loads(data)
        except Exception as e:
            self.__log(str(e))
            return self.__init_cfg()

    def __save_cfg(self, cfg: dict):
        with open(self.__cfg_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(cfg))

    def __log(self, s):
        with open(self.__log_file, 'w+', encoding='utf-8') as f:
            f.write(s + '\n')

    def __backup(self, cluster_name):
        cluster_path = '%s/%s' % (CLUSTER_DIR, cluster_name)
        if os.path.exists(cluster_path):
            file_name = strftime('Cluster_%Y-%m-%d-%H-%M-%S', localtime())
            run_cmd('mkdir -p %s' % CLUSTER_BACKUP_DIR,
                    'tar -czvf %s/%s.tar.gz %s' % (CLUSTER_BACKUP_DIR, file_name, cluster_path))



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
#         python3 ./mod_add.py "${cluster_dir}/${cluster_name}/Master/modoverrides.lua" "modoverrides"
#         set_mod
#         echo "Add success."
#     elif [ $chose == "2" ]
#     then
#         echo "Print Mod ID:"
#         python3 ./mod_add.py "${cluster_dir}/${cluster_name}/Master/modoverrides.lua" "modid"
#         set_mod
#         echo "Add success."
#     elif [ $chose == "3" ]     # Exit
#     then
#         echo "Exit."
#     else
#         echo "Command Error."
#     fi

# elif user_in == '7':  # Run Custom
# then
#     clear
#     echo "Which to run?"
#     echo "  (1) MyDediServer2"
#     echo "  (2) Single_world"
#     echo "  (3) Reforged"
#     echo "  (4) Exit"
#     read chose
#     if [ $chose == "1" ]
#     then
#         cluster_name="MyDediServer2"
#         set_mod
#         get_run_shared
#         "${run_shared[@]}" -shard Caves  | sed 's/^/Caves:  /' &
#         "${run_shared[@]}" -shard Master | sed 's/^/Master: /'
#     elif [ $chose == "2" ]
#     then
#         set_mod
#         get_run_shared
#         "${run_shared[@]}" -shard Master | sed 's/^/Master: /'
#     elif [ $chose == "3" ]
#     then
#         cluster_name="Reforged"
#         set_mod
#         get_run_shared
#         "${run_shared[@]}" -shard Master | sed 's/^/Master: /'
#     elif [ $chose == "4" ]
#     then
#         echo "Exit."
#     else
#         echo "Command Error."
#     fi



if __name__ == '__main__':
    dst_server = Server()
    dst_server.run()
