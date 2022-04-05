import unittest


class TestFilter(unittest.TestCase):
    def test_filter_value_none(self):
        data = {
            'a': 0,
            'b': None,
            'c': {
                'b': 1,
                'e': None,
                'f': {
                    'g': 2,
                    'h': None
                }
            }

        }
        res = filter_value_none(data)
        self.assertDictEqual(res, {
            'a': 0,
            'c': {
                'b': 1,
                'f': {
                    'g': 2
                }
            }
        })

    def test_deep_update(self):
        data = {
            'a': 0,
            'c': {
                'b': 1,
                'f': {
                    'g': 2
                }
            }

        }
        deep_update(data, {
            'a': 3,
            'c': {
                'b': 4,
                'f': {},
                'j': 6
            },
            'h': {
                'i': 5
            }
        })
        self.assertDictEqual(data, {
            'a': 3,
            'c': {
                'b': 4,
                'f': {
                    'g': 2
                },
                'j': 6
            },
            'h': {
                'i': 5
            }
        })
