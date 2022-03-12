from datetime import datetime, timedelta
import time
import unittest

import logging

import sys

import main_smart_meter as meter

class Main_Test(unittest.TestCase):

                                                                                                                        
    def test_dummy(self):
        self.assertEqual(True, True)
        logging.warning("we passed this basic test!")

    def test_0_0_0_new_log_info(self):
        meter.do_trace = False

        with self.assertLogs() as captured:
            #by default an info (OK) log should not come through
            meter.new_log("OK: TestLog, all is fine!")
            self.assertEqual(len(captured.records), 0) # This Message should not come through, by default info logging is off

            #with trace this should come through
            meter.do_trace = True
            meter.new_log("OK: TestLog, all is fine!")
            self.assertEqual(len(captured.records), 1) # This Message should not come through, by default info logging is off
            self.assertEqual(captured.output[0][:4], "INFO")

    def test_0_0_1_new_log_warning(self):
        meter.do_trace = False

        with self.assertLogs() as captured:
            # A warning should always be registered
            meter.new_log("WARNING: TestLog, we have a warning!")

            #captured.
            self.assertEqual(len(captured.records), 1) # This Message should not come through, by default info logging is off
            self.assertEqual(captured.output[0][:7], "WARNING")

    def test_0_0_2_new_log_error(self):
        meter.do_trace = False

        with self.assertLogs() as captured:
            # A warning should always be registered
            meter.new_log("ERROR: TestLog, we have an error!")

            #captured.
            self.assertEqual(len(captured.records), 1) # This Message should not come through, by default info logging is off
            self.assertEqual(captured.output[0][:5], "ERROR")

    def test_0_1_0_new_log_exception(self):
        meter.do_trace = False

        with self.assertLogs() as captured:

            meter.new_log("OK: TestLog, we have an error!", ZeroDivisionError)
            self.assertEqual(len(captured.records), 0) # This Message should not come through, by default info logging is off            

            meter.do_trace = True
            meter.new_log("OK: TestLog, we have an error!", ZeroDivisionError)
            self.assertEqual(len(captured.records), 2) # This Message should not come through, by default info logging is off
            self.assertEqual(captured.output[0][:4], "INFO")
            self.assertEqual(captured.output[1][:4], "INFO")
            self.assertIn('ZeroDivisionError', captured.output[1])


    def test_0_1_1_new_log_exception(self):
        meter.do_trace = False

        with self.assertLogs() as captured:
            meter.new_log("WARNING: TestLog, we have an error!", ZeroDivisionError)
            self.assertEqual(len(captured.records), 2) # This Message should not come through, by default info logging is off
            self.assertEqual(captured.output[0][:7], "WARNING")
            self.assertEqual(captured.output[1][:7], "WARNING")
            self.assertIn('ZeroDivisionError', captured.output[1])

    def test_0_1_2_new_log_exception(self):
        meter.do_trace = False

        with self.assertLogs() as captured:
            meter.new_log("ERROR: TestLog, we have an error!", ZeroDivisionError)
            self.assertEqual(len(captured.records), 2) # This Message should not come through, by default info logging is off
            self.assertEqual(captured.output[0][:5], "ERROR")
            self.assertEqual(captured.output[1][:5], "ERROR")
            self.assertIn('ZeroDivisionError', captured.output[1])

    def test_1_0_0_update_version(self):
        meter.get_influx().init_influx('user', "pass", "host", in_local_test=True)

        meter.update_version("SmartMeter", "Some_Home")
        self.assertEqual(len(meter.get_influx().data_points), 1)


if __name__ == '__main__':

    unittest.main()

