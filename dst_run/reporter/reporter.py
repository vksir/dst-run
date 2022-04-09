from dst_run.common.log import log


__all__ = ['REPORTER']


class Reporter:
    @staticmethod
    def deal_with_msg(msg: str):
        """
        [Join Announcement] 󰀃Villkiss
        [Leave Announcement] 󰀃Villkiss
        [Death Announcement] 󰀃Villkiss 死于： 时间流逝。她变成了可怕的鬼魂！
        [Resurrect Announcement] 󰀃Villkiss 复活自： TMIP 控制台.
        [Say] (xxxxxx) 󰀃Villkiss: hello
        [Announcement] hello
        Starting master server
        Sim paused
        Shutting down
        """
        log.info(f'report msg: msg={msg}')

    def _deal_with_player_msg(self, msg):
        pass

    def _deal_with_server_msg(self, msg):
        pass

    def report(self, msg: str):
        pass


REPORTER = Reporter()
