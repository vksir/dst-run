import argparse
import log
from tools import run_cmd
from dst_run import Controller, STEAMCMD_HOME


def install():
    try:
        run_cmd('apt install libstdc++6:i386 libgcc1:i386 libcurl4-gnutls-dev:i386 -y',
                'mkdir -p %s' % STEAMCMD_HOME,
                'wget "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz"',
                'tar -xzvf steamcmd_linux.tar.gz',
                'rm steamcmd_linux.tar.gz', cwd=STEAMCMD_HOME, sudo=True)
        dst_server = Controller()
        dst_server.server_update()
    except Exception as e:
        log.error('install: {}'.format(e))
        print(e)
        exit(1)
