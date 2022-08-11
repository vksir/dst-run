import re

import httpx
from dst_run.common.log import log
from dst_run.common.constants import Constants
from dst_run.confs.confs import CONF


class Reporter:
    def report_raw_message(self, process: str, raw_message: str):
        msg, level = self._deal_with_raw_message(raw_message)
        if msg is None:
            return
        is_need_report = self._filter_level(level)
        if not is_need_report:
            return
        self.report(f'[{process}] {msg}', level)

    @staticmethod
    def _deal_with_raw_message(raw_message: str):
        log.debug(f'report raw_message: raw_message={raw_message}')
        regex = [
            {
                'pattern': r'\[Join Announcement\] (.*)',
                'template': '%s 加入世界',
                'level': 'info'
            },
            {
                'pattern': r'\[Leave Announcement\] (.*)',
                'template': '%s 离开世界',
                'level': 'info'
            },
            {
                'pattern': r'\[Death Announcement\] (.*) 死于： (.*)。',
                'template': '%s 死于：%s',
                'level': 'debug'
            },
            {
                'pattern': r'\[Resurrect Announcement\] (.*) 复活自： (.*).',
                'template': '%s 复活自：%s',
                'level': 'debug'
            },
            {
                'pattern': r'\[Announcement\] (.*)',
                'template': '全服宣告：%s',
                'level': 'debug'
            },
            {
                'pattern': 'Shard server started',
                'template': '服务器启动成功',
                'level': 'error'
            },
            {
                'pattern': 'Shutting down',
                'template': '服务器停止运行',
                'level': 'error'
            },
            {
                'pattern': 'Sim paused',
                'template': '世界暂停',
                'level': 'warning'
            }
        ]
        for item in regex:
            pattern = item['pattern']
            template = item['template']
            level = item['level']
            res = re.search(pattern, raw_message)
            if not res:
                continue
            msg = template % res.groups()
            return msg, level
        return None, None

    @staticmethod
    def _filter_level(level: str):
        report_level = CONF.common.report_level
        level_num = {
            'debug': 10,
            'info': 20,
            'warning': 30,
            'error': 40,
            'critical': 50
        }
        return level_num[level] > level_num[report_level]

    @staticmethod
    def report(msg: str, level: str):
        host = CONF.common.report_host
        port = CONF.common.report_port
        url = f'http://{host}:{port}/{Constants.COMPONENT}'
        try:
            res = httpx.post(url, json={
                'nickname': CONF.common.nickname,
                'uuid': CONF.common.uuid,
                'msg': msg,
                'level': level
            })
        except Exception as e:
            log.error(f'report failed: msg={msg}, level={level}, e={e}')
            return
        if res.status_code == 200:
            log.info(f'report succeed: msg={msg}, level={level}')
        else:
            log.error(f'report failed: msg={msg}, level={level}, '
                      f'status={res.status_code}, content={res.content}')


REPORTER = Reporter()
