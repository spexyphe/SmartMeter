from datetime import datetime, timedelta
import time
import unittest
import sys
import os
import logging

from unittest import mock

import sys

try:
    import module_env_var as env_var
except Exception as e:
    logging.error(str(e))

    try:
        from . import module_env_var as env_var
    except Exception as ex:
        logging.error(str(ex))

logging.warning("start with env_var")

class env_var_Test(unittest.TestCase):

    def test_dummy(self):
        self.assertEqual(True, True)
        logging.warning("we passed this basic test!")

    def test_0_0_0_new_log_info(self):

        with self.assertLogs() as captured:
            #by default an info (OK) log should not come through
            env_var.new_log("OK: TestLog, all is fine!")
            self.assertEqual(len(captured.records), 1) # This Message should not come through, by default info logging is off
            self.assertEqual(captured.output[0][:4], "INFO")

    def test_0_0_1_new_log_warning(self):
        with self.assertLogs() as captured:
            # A warning should always be registered
            env_var.new_log("WARNING: TestLog, we have a warning!")

            #captured.
            self.assertEqual(len(captured.records), 1) # This Message should not come through, by default info logging is off
            self.assertEqual(captured.output[0][:7], "WARNING")

    def test_0_0_2_new_log_error(self):

        with self.assertLogs() as captured:
            # A warning should always be registered
            env_var.new_log("ERROR: TestLog, we have an error!")

            #captured.
            self.assertEqual(len(captured.records), 1) # This Message should not come through, by default info logging is off
            self.assertEqual(captured.output[0][:5], "ERROR")

    def test_0_1_0_new_log_exception(self):

        with self.assertLogs() as captured:

            env_var.new_log("OK: TestLog, we have an error!", ZeroDivisionError)
            self.assertEqual(len(captured.records), 2) # This Message should not come through, by default info logging is off
            self.assertEqual(captured.output[0][:4], "INFO")
            self.assertEqual(captured.output[1][:4], "INFO")
            self.assertIn('ZeroDivisionError', captured.output[1])


    def test_0_1_1_new_log_exception(self):
        with self.assertLogs() as captured:
            env_var.new_log("WARNING: TestLog, we have an error!", ZeroDivisionError)
            self.assertEqual(len(captured.records), 2) # This Message should not come through, by default info logging is off
            self.assertEqual(captured.output[0][:7], "WARNING")
            self.assertEqual(captured.output[1][:7], "WARNING")
            self.assertIn('ZeroDivisionError', captured.output[1])

    def test_0_1_2_new_log_exception(self):

        with self.assertLogs() as captured:
            env_var.new_log("ERROR: TestLog, we have an error!", ZeroDivisionError)
            self.assertEqual(len(captured.records), 2) # This Message should not come through, by default info logging is off
            self.assertEqual(captured.output[0][:5], "ERROR")
            self.assertEqual(captured.output[1][:5], "ERROR")
            self.assertIn('ZeroDivisionError', captured.output[1])

    def test_1_0_0_env_defaults(self):
        self.assertEqual((False, False, True, True), env_var.load_env_var_sys())

    def test_1_0_1_env_reversed_input(self):
        with mock.patch.dict(os.environ, {"do_trace": "False", "is_local_test": "True", "is_var_run": "False"}):
            self.assertEqual((True, True, False, False), env_var.load_env_var_sys())

    def test_1_0_1_env_default_as_input(self):
        with mock.patch.dict(os.environ, {"do_trace": "True", "is_local_test": "False", "is_var_run": "True"}):
            self.assertEqual((True, False, True, True), env_var.load_env_var_sys())

    def test_1_1_0_env_defaults(self):
        #test default output without any env vars set
        self.assertEqual(env_var.load_env_var_modbus(), (False, False, '/dev/ttyUSB0', 115200, 'E', ''))

    def test_1_1_1_env_defaults(self):
        #env variable input combinations
        var_set = [
        {"modbus_auto_detect": "False"},
        {"modbus_auto_detect": "True"},   
        {"modbus_auto_detect": "True", "modbus_device": '/dev/ttyUSB0'},
        {"modbus_auto_detect": "True", "modbus_device": '/dev/ttyUSB1'},
        {"modbus_auto_detect": "True", "modbus_device": '/dev/ttyUSB1', "modbus_baud": '115200'},
        {"modbus_auto_detect": "True", "modbus_device": '/dev/ttyUSB1', "modbus_baud": '110000'},
        {"modbus_auto_detect": "True", "modbus_device": '/dev/ttyUSB1', "modbus_baud": '110000', "modbus_parity": 'E'},
        {"modbus_auto_detect": "True", "modbus_device": '/dev/ttyUSB1', "modbus_baud": '110000', "modbus_parity": 'N'},
        {"modbus_auto_detect": "True", "modbus_device": '/dev/ttyUSB1', "modbus_baud": '110000', "modbus_parity": 'N', "modbus_variables": ''},
        {"modbus_auto_detect": "True", "modbus_device": '/dev/ttyUSB1', "modbus_baud": '110000', "modbus_parity": 'N', "modbus_variables": 'a_var'}]

        #what answers do we expect?
        loaded_set = [
        (False, False, '/dev/ttyUSB0', 115200, 'E', ''),
        (False, True, '/dev/ttyUSB0', 115200, 'E', ''),
        (False, True,  '/dev/ttyUSB0', 115200, 'E', ''), 
        (False, True,  '/dev/ttyUSB1', 115200, 'E', ''),
        (False, True,  '/dev/ttyUSB1', 115200, 'E', ''),
        (False, True,  '/dev/ttyUSB1', 110000, 'E', ''),
        (False, True,  '/dev/ttyUSB1', 110000, 'E', ''),
        (False, True,  '/dev/ttyUSB1', 110000, 'N', ''),
        (True, True,  '/dev/ttyUSB1', 110000, 'N', ''),
        (True, True,  '/dev/ttyUSB1', 110000, 'N', 'a_var')
        ]

        # internal sanity check
        # do the predefined sets match in length?
        self.assertEqual(len(var_set), len(loaded_set))

        for i in range(0, len(var_set)):
            #demo print
            print(i)
            #print(var_set[i])
            
            with mock.patch.dict(os.environ, var_set[i]):
                #demo print
                #print(env_var.load_env_var_modbus())

                #does the environment var input match the expected output
                self.assertEqual(env_var.load_env_var_modbus(), loaded_set[i])

    def test_1_2_0_env_defaults(self):
        #test default output without any env vars set
        self.assertEqual(env_var.load_env_var_influx(), (False,'',8086,'default_org','default_token','default_bucket', 'default_measurement','default_host'))

    def test_1_2_1_env_defaults(self):

        #env variable input combinations
        var_set = [{"influx_url": 'a_random_url'},
        {"influx_url": 'a_not_random_url'},
        {"influx_url": 'a_not_random_url', "influx_port": '7100'},
        {"influx_url": 'a_not_random_url', "influx_port": '9100'},
        {"influx_url": 'a_not_random_url', "influx_port": '9100', "influx_org": 'a_random_org'},
        {"influx_url": 'a_not_random_url', "influx_port": '9100', "influx_org": 'a_org'},
        {"influx_url": 'a_not_random_url', "influx_port": '9100', "influx_org": 'a_org', "influx_token": 'abc_000'},
        {"influx_url": 'a_not_random_url', "influx_port": '9100', "influx_org": 'a_org', "influx_token": 'abc_000'},
        {"influx_url": 'a_not_random_url', "influx_port": '9100', "influx_org": 'a_org', "influx_token": 'abc_000', "influx_bucket": 'a_random_bucket'},
        {"influx_url": 'a_not_random_url', "influx_port": '9100', "influx_org": 'a_org', "influx_token": 'abc_000', "influx_bucket": 'not_a_random_bucket'},
        {"influx_url": 'a_not_random_url', "influx_port": '9100', "influx_org": 'a_org', "influx_token": 'abc_000', "influx_bucket": 'not_a_random_bucket', "influx_measurement": 'a_random_measurement'},
        {"influx_url": 'a_not_random_url', "influx_port": '9100', "influx_org": 'a_org', "influx_token": 'abc_000', "influx_bucket": 'not_a_random_bucket', "influx_measurement": 'not_a_random_measurement'},
        {"influx_url": 'a_not_random_url', "influx_port": '9100', "influx_org": 'a_org', "influx_token": 'abc_000', "influx_bucket": 'not_a_random_bucket', "influx_measurement": 'not_a_random_measurement', "influx_host": 'a_user_host'},
        {"influx_url": 'a_not_random_url', "influx_port": '9100', "influx_org": 'a_org', "influx_token": 'abc_000', "influx_bucket": 'not_a_random_bucket', "influx_measurement": 'not_a_random_measurement', "influx_host": 'a_power_host'}]

        #what answers do we expect?
        loaded_set = [
        (False,'a_random_url',8086,'default_org','default_token','default_bucket','default_measurement','default_host'), 
        (False,'a_not_random_url',8086,'default_org','default_token','default_bucket','default_measurement','default_host'),
        (False,'a_not_random_url',7100,'default_org','default_token','default_bucket','default_measurement','default_host'),
        (False,'a_not_random_url',9100,'default_org','default_token','default_bucket','default_measurement','default_host'),
        (False,'a_not_random_url',9100,'a_random_org','default_token','default_bucket','default_measurement','default_host'),
        (False,'a_not_random_url',9100,'a_org','default_token','default_bucket','default_measurement','default_host'),
        (False,'a_not_random_url',9100,'a_org','abc_000','default_bucket','default_measurement','default_host'),
        (False,'a_not_random_url',9100,'a_org','abc_000','default_bucket','default_measurement','default_host'), 
        (False,'a_not_random_url',9100,'a_org','abc_000','a_random_bucket','default_measurement','default_host'),
        (False,'a_not_random_url',9100,'a_org','abc_000','not_a_random_bucket','default_measurement','default_host'),
        (False,'a_not_random_url',9100,'a_org','abc_000','not_a_random_bucket','a_random_measurement','default_host'),
        (False,'a_not_random_url',9100,'a_org','abc_000','not_a_random_bucket','not_a_random_measurement','default_host'),
        (True,'a_not_random_url',9100,'a_org','abc_000','not_a_random_bucket','not_a_random_measurement','a_user_host'),
        (True,'a_not_random_url',9100,'a_org','abc_000','not_a_random_bucket','not_a_random_measurement','a_power_host')
        ]

        # internal sanity check
        # do the predefined sets match in length?
        self.assertEqual(len(var_set), len(loaded_set))

        self.assertEqual(env_var.load_env_var_influx(), (False,'',8086,'default_org','default_token','default_bucket','default_measurement','default_host'))

        for i in range(0, len(var_set)):
            #demo print
            print(i)
            #print(var_set[i])
            
            with mock.patch.dict(os.environ, var_set[i]):
                #demo print
                #print(env_var.load_env_var_influx())

                with self.subTest(str(i)):
                    #does the environment var input match the expected output
                    self.assertEqual(env_var.load_env_var_influx(), loaded_set[i])

if __name__ == '__main__':

    unittest.main()

