from datetime import datetime, timedelta
import time
import unittest
import sys
import os
import logging
import serial

import sys

try:
    # Python >= 3.3 
    from unittest import mock
except ImportError:
    logging.error("could not import unittest - mock")
    # Python < 3.3
    #import mock

try:
    import module_find_usb as find_usb
except Exception as e:
    logging.error(str(e))

    try:
        from . import module_find_usb as find_usb
    except Exception as ex:
        logging.error(str(ex))

logging.warning("start with find_usb")

class env_var_Test(unittest.TestCase):

    def test_dummy(self):
        self.assertEqual(True, True)
        logging.warning("we passed this basic test!")

    #check if the init of the serial parameters is succesfull
    def test_0_0_0_init(self):
        find_usb.init_parameters(10000, serial.PARITY_EVEN, serial.SEVENBITS, serial.STOPBITS_ONE, 0,0,20 )
        
        # was the serial object created
        self.assertIsNotNone(find_usb.ser)

        # where the parameters stored correctly
        self.assertEqual(find_usb.ser.baudrate,  10000)
        self.assertEqual(find_usb.ser.parity, serial.PARITY_EVEN)
        self.assertEqual(find_usb.ser.bytesize,  serial.SEVENBITS)
        self.assertEqual(find_usb.ser.stopbits,  serial.STOPBITS_ONE)
        self.assertEqual(find_usb.ser.xonxoff,  0)
        self.assertEqual(find_usb.ser.rtscts,  0)
        self.assertEqual(find_usb.ser.timeout,  20)

#    # @mock.patch('find_usb.os.listdir')
#     def test_1_0_0_find(self):
#         with mock.patch('os.listdir') as mocked_listdir:

#             mocked_listdir.return_value = ['ttyUSB0', 'ttyUSB1']
#             self.assertIsNone(find_usb.find_correct_usb("ttyUSB0"))
#             #self.assertEqual(len(mocked_listdir), 2)

#         #this might not work
#         #mock_listdir.return_value = ['ttyUSB0']
#         #self.assertIsNone(find_usb.find_correct_usb("test"))
#         logging.warning("test")
        



if __name__ == '__main__':
    unittest.main()

