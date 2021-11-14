import os


HOME = os.environ.get('HOME')

PROGRAM_HOME = f'{HOME}/dst_run'
TEMPLATE_HOME = f'{HOME}/dst_run/cluster_template'

PROGRAM_DATA_HOME = f'{HOME}/.dst_run'
CFG_PATH = f'{HOME}/.dst_run/config.json'
LOG_PATH = f'{HOME}/.dst_run/dst_run.log'
USER_TEMPLATE_HOME = f'{HOME}/.dst_run/cluster_template'
GAME_LOG_HOME = f'{HOME}/.dst_run/log'
GAME_LOG_PATH = f'{HOME}/.dst_run/log/log.txt'
GAME_LOG_BACKUP_HOME = f'{HOME}/.dst_run/log/backup'

STEAMCMD_HOME = f'{HOME}/steamcmd'
DST_HOME = f'{HOME}/dst'
CLUSTERS_HOME = f'{HOME}/.klei/DoNotStarveTogether'
CLUSTERS_BACKUP_HOME = f'{HOME}/.klei/DoNotStarveTogether/backup'
MASTER_WORLD_SETTING_PATH = f'{HOME}/.klei/DoNotStarveTogether/leveldataoverride.lua'
CAVES_WORLD_SETTING_PATH = f'{HOME}/.klei/DoNotStarveTogether/leveldataoverride.lua'

# exitcode
EXIT_SUCCESS = 0
EXIT_FAILED = 1


# choice code
CHOICE_EXIT = -1
CHOICE_DEFAULT = 0
CHOICE_YES = True
CHOICE_NO = False


# special variable
REFORGED = 'reforged'
NAME_SURROUND = '󰀅'
MASTER = 'Master'
CAVES = 'Caves'
DEFAULT = 'default'
EXIT = 'Exit'
TRUE = 'true'
FALSE = 'false'


# cfg key
CLUSTER_KEY = 'cluster'
ENABLE_REFORGED_KEY = 'enable_reforged'
ENABLE_CAVES_KEY = 'enable_caves'
ENABLE_64BIT_KEY = 'enable_64-bit'
CLUSTER_TOKEN_KEY = 'cluster_token'
VERSION_KEY = 'version'
TEMPLATE_KEY = 'template'

EDITOR_KEY = 'editor'
VIM, NANO = 'vim', 'nano'

ENDLESS_MODE = 'endless'
GAME_MODE_KEY = 'game_mode'
PVP_KEY = 'pvp'

MAX_PLAYERS_KEY = 'max_players'
ROOM_NAME_KEY = 'room_name'
ROOM_PASSWORD_KEY = 'room_password'
ROOM_DESCRIPTION_KEY = 'root_description'
TICK_RATE_KEY = 'tick_rate'
ADMIN_LIST_KEY = 'admin_list'

WORLD_SIZE_KEY = 'world_size'
SPECIAL_EVENT_KEY = 'special_event'


# choice key
OTHERS_KEY = 'Others'
EXIT_KEY = 'Exit'

WHITE_LIST_KEY = 'white_list'


# http server
IP = '127.0.0.1'
PORT = 5800
