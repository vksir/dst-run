from unittest.runner import TextTestRunner
from unittest.suite import TestSuite
from unittest.loader import TestLoader

if __name__ == '__main__':
    loader = TestLoader()
    discover = loader.discover(start_dir='test_dst_run', pattern='test*.py')
    suite = TestSuite()
    suite.addTest(discover)
    runner = TextTestRunner()
    runner.run(suite)
