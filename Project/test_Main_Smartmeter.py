from datetime import datetime, timedelta
import time
import unittest
import sys

from main_smart_meter import meter

class TestStringMethods(unittest.TestCase):

    Lines=[["1-0:1.8.1(002053.081*kWh)'",2053.081], ["b'0-0:96.7.9(00087)\r\n'", 87], ["b'1-0:21.7.0(00.030*kW)\r\n'", 0.03], ["b'0-1:24.2.1(211223155000W)(02418.351*m3)\r\n'",2418.351]]


                                                                                                                                          
 

    mainmodule = meter()

    def test_1_0_0_func_calc_amp(self):
        self.assertEqual(self.mainmodule.func_calc_amp(943.0 ,0.0 ,None), 0)
        self.assertEqual(self.mainmodule.func_calc_amp(None,None,230.0), 0)
        self.assertEqual(self.mainmodule.func_calc_amp(None,None,None), 0)
    
    def test_1_0_1_func_calc_amp(self):
        self.assertEqual(self.mainmodule.func_calc_amp(943.0,0.0,230.0), 4.1)
        self.assertEqual(self.mainmodule.func_calc_amp(None,943.0,230.0), 4.1)
        self.assertEqual(self.mainmodule.func_calc_amp(943.0,None,230.0), 4.1)




    # run a number of tests on parsing
    def test_8_0_0_Parse(self):
        
        for line in self.Lines:

            self.assertEqual(self.mainmodule.parse_line(line[0]), line[1])

    # run a number of tests on parsing
    def test_9_0_0_Parse(self):
        volt = self.mainmodule.parse_line("1-0:32.7.0(235.0*V)")
        cons = (self.mainmodule.parse_line("1-0:21.7.0(00.102*kW)") * 1000)
        prod = (self.mainmodule.parse_line("1-0:22.7.0(00.000*kW)" ) * 1000)
        print(self.mainmodule.func_calc_amp(cons, prod, volt))




if __name__ == '__main__':
    unittest.main()

