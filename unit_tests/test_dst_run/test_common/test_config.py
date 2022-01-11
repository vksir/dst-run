import builtins
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch
from dst_run.routes.config import WorldCfg


class TestWorldCfg(unittest.TestCase):
    def setUp(self) -> None:
        self.test_obj = WorldCfg()

    @patch.object(builtins, 'open')
    def test_read(self, mock_open):
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




