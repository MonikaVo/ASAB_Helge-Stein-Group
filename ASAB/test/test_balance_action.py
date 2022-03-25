import unittest
from tests.filesForTests import config_test
from utility.helpers import doAppends, loadFile
conf = config_test.config
doAppends(conf)

import unittest
from testfixtures import compare
import serial

from driver import balance_driver
from action import balance_action


class test_balance_action(unittest.TestCase):

    def test_readBalance(self):
        balance2 = balance_driver.balance(simulated=True)

        reading_result = balance2.readBalance()
        reading_target = balance2.port.target

        self.assertEqual(first=reading_target, second=reading_result, msg="Readings do not match.")

if __name__ == "__main__":
    unittest.main(verbosity=2)