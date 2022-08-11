import unittest
from unittest.mock import patch
from dst_run.reporter.reporter import Reporter


patch('dst_run.common.log.log.debug').start()


class TestReporter(unittest.TestCase):
    def setUp(self) -> None:
        self.test_obj = Reporter()

    def test_deal_with_raw_message(self):
        raw_message = '[Join Announcement] player'
        msg, _ = self.test_obj._deal_with_raw_message(raw_message)
        self.assertEqual('player 加入世界', msg)

        raw_message = '[Leave Announcement] player'
        msg, _ = self.test_obj._deal_with_raw_message(raw_message)
        self.assertEqual('player 离开世界', msg)

        raw_message = '[Death Announcement] player 死于： 时间流逝。她变成了可怕的鬼魂！'
        msg, _ = self.test_obj._deal_with_raw_message(raw_message)
        self.assertEqual('player 死于：时间流逝', msg)

        raw_message = '[Resurrect Announcement] player 复活自： TMIP 控制台.'
        msg, _ = self.test_obj._deal_with_raw_message(raw_message)
        self.assertEqual('player 复活自：TMIP 控制台', msg)

        raw_message = '[Announcement] hello world'
        msg, _ = self.test_obj._deal_with_raw_message(raw_message)
        self.assertEqual('全服宣告：hello world', msg)

        raw_message = 'Shard server started'
        msg, _ = self.test_obj._deal_with_raw_message(raw_message)
        self.assertEqual('服务器启动成功', msg)

        raw_message = 'Shutting down'
        msg, _ = self.test_obj._deal_with_raw_message(raw_message)
        self.assertEqual('服务器停止运行', msg)

        raw_message = 'Sim paused'
        msg, _ = self.test_obj._deal_with_raw_message(raw_message)
        self.assertEqual('世界暂停', msg)
