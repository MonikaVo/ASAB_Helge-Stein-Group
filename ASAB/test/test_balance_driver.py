import unittest
from tests.filesForTests import config_test
from utility.helpers import doAppends, loadFile
conf = config_test.config
doAppends(conf)

import unittest
from testfixtures import compare
import serial

from driver import balance_driver

class test_balance_driver(unittest.TestCase):

    def test___init__(self):
        port_target = conf["balanceDriver"]["serialPort"]
        settings_target = conf["balanceDriver"]["settings"]

        balance1 = balance_driver.balance(simulated=False)

        port_result = balance1.port.port
        settings_result = balance1.port.get_settings()

        self.assertEqual(first=port_target, second=port_result, msg="Port is not correct")
        self.assertDictEqual(d1=settings_target, d2=settings_result, msg="Settings do not match")


    
    def test_readBalance(self):
        balance2 = balance_driver.balance(simulated=True)

        reading_result = balance2.readBalance()
        reading_target = balance2.port.target

        self.assertEqual(first=reading_target, second=reading_result, msg="Readings do not match.")

if __name__ == "__main__":
    unittest.main(verbosity=2)