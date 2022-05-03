import builtins
from io import StringIO
from unittest import TestCase
from unittest.mock import patch
from dst_run.app.routes import BaseCfg
from dst_run.app.routes import RoomCfgHandler
from dst_run.app.routes import WorldCfgHandler


class TestRoomCfgHandler(TestCase):
    @patch('dst_run.routes.config.BaseCfg.save_cfg')
    @patch('dst_run.routes.config.BaseCfg.read_cfg')
    @patch('os.path.exists')
    def setUp(self, mock_exists, mock_read_cfg, mock_save_cfg) -> None:
        mock_exists.return_value = False
        base_cfg = BaseCfg()
        self.test_obj = RoomCfgHandler(base_cfg)

    def test_room(self):
        init_data = self.test_obj._get_init_data()
        data = self.test_obj
        self.assertDictEqual(init_data, dict(data))


class TestWorldCfgHandler(TestCase):
    @patch('yaml.load')
    @patch('os.path.exists')
    def setUp(self, mock_exists, mock_load) -> None:
        mock_load.return_value = {}
        mock_exists.return_value = True
        base_cfg = BaseCfg()
        self.test_obj = WorldCfgHandler(base_cfg)

    @patch.object(builtins, 'open')
    def test__load(self, mock_open):
        mock_open.return_value = StringIO("""
        return {
          overrides={
            key1="value1",
            key2="value2"
          }
        }""")
        res = self.test_obj._read('')
        self.assertDictEqual(res, {
            'key1': 'value1',
            'key2': 'value2'
        })




