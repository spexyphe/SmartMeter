from datetime import datetime, timedelta
import time
import unittest
import sys

from Main_SmartMeter import Meter

class TestStringMethods(unittest.TestCase):

    Lines=[["1-0:1.8.1(002053.081*kWh)'",2053.081], ["b'0-0:96.7.9(00087)\r\n'", 87], ["b'1-0:21.7.0(00.030*kW)\r\n'", 0.03], ["b'0-1:24.2.1(211223155000W)(02418.351*m3)\r\n'",2418.351]]

    
    # run a number of tests on parsing
    def test_1_0_0_Parse(self):
        
        Parser = Meter().parse_line

        for line in self.Lines:

            self.assertEqual(Parser(line[0]), line[1])

if __name__ == '__main__':
    unittest.main()

