from datetime import datetime, timedelta
import time
import unittest
import sys
import logging
logging.warning("start with transform")

import sys

try:
    import module_transform as transform
except Exception as e:
    logging.error(str(e))

    try:
        from . import module_transform as transform
    except Exception as ex:
        logging.error(str(ex))

try:
    import module_influx as influx
except Exception as e:
    logging.error(str(e))

    try:
        from . import module_influx as influx
    except Exception as ex:
        logging.error(str(ex))


class Transform_Test(unittest.TestCase):

    Line=["1-0:1.8.1(002053.081*kWh)'",2053.081]

    Lines=[["1-0:1.8.1(002053.081*kWh)'",2053.081], ["b'0-0:96.7.9(00087)\r\n'", 87], ["b'1-0:21.7.0(00.030*kW)\r\n'", 0.03], ["b'0-1:24.2.1(211223155000W)(02418.351*m3)\r\n'",2418.351]]


    # run a number of tests on parsing
    def test_0_0_0_Dummy(self):

        
        self.assertEqual(True, True, "Have fun with this one, True != True")

    def test_1_0_0_Init(self):
        influx.init_influx("None", "None", "None", 8086, "None", True, True)
        transform.init_transform()
        transform.set_influx_module(influx, "smartmeter", "my_tiny_house")
        self.assertIsNotNone(transform.transform_mem_state)

    def test_0_0_0_new_log_info(self):
        transform.log_transform = False

        with self.assertLogs() as captured:
            #by default an info (OK) log should not come through
            transform.new_log("OK: TestLog, all is fine!")
            self.assertEqual(len(captured.records), 0) # This Message should not come through, by default info logging is off

            #with trace this should come through
            transform.log_transform = True
            transform.new_log("OK: TestLog, all is fine!")
            self.assertEqual(len(captured.records), 1) # This Message should not come through, by default info logging is off
            self.assertEqual(captured.output[0][:4], "INFO")

    def test_0_0_1_new_log_warning(self):
        transform.log_transform = False

        with self.assertLogs() as captured:
            # A warning should always be registered
            transform.new_log("WARNING: TestLog, we have a warning!")

            #captured.
            self.assertEqual(len(captured.records), 1) # This Message should not come through, by default info logging is off
            self.assertEqual(captured.output[0][:7], "WARNING")

    def test_0_0_2_new_log_error(self):
        transform.log_transform = False

        with self.assertLogs() as captured:
            # A warning should always be registered
            transform.new_log("ERROR: TestLog, we have an error!")

            #captured.
            self.assertEqual(len(captured.records), 1) # This Message should not come through, by default info logging is off
            self.assertEqual(captured.output[0][:5], "ERROR")

    def test_0_1_0_new_log_exception(self):
        transform.log_transform  = False

        with self.assertLogs() as captured:

            transform.new_log("OK: TestLog, we have an error!", ZeroDivisionError)
            self.assertEqual(len(captured.records), 0) # This Message should not come through, by default info logging is off            

            transform.log_transform  = True
            transform.new_log("OK: TestLog, we have an error!", ZeroDivisionError)
            self.assertEqual(len(captured.records), 2) # This Message should not come through, by default info logging is off
            self.assertEqual(captured.output[0][:4], "INFO")
            self.assertEqual(captured.output[1][:4], "INFO")
            self.assertIn('ZeroDivisionError', captured.output[1])


    def test_0_1_1_new_log_exception(self):
        transform.log_transform = False

        with self.assertLogs() as captured:
            transform.new_log("WARNING: TestLog, we have an error!", ZeroDivisionError)
            self.assertEqual(len(captured.records), 2) # This Message should not come through, by default info logging is off
            self.assertEqual(captured.output[0][:7], "WARNING")
            self.assertEqual(captured.output[1][:7], "WARNING")
            self.assertIn('ZeroDivisionError', captured.output[1])

    def test_0_1_2_new_log_exception(self):
        transform.log_transform = False

        with self.assertLogs() as captured:
            transform.new_log("ERROR: TestLog, we have an error!", ZeroDivisionError)
            self.assertEqual(len(captured.records), 2) # This Message should not come through, by default info logging is off
            self.assertEqual(captured.output[0][:5], "ERROR")
            self.assertEqual(captured.output[1][:5], "ERROR")
            self.assertIn('ZeroDivisionError', captured.output[1])


    #happy flow - succesfully create a point
    def test_3_0_0_create_data_point_locally(self):
        # unit test pre-cleanup
        influx.clear_points()
        transform.clear_mem()  

        # add the point
        transform.create_data_point_locally("test_name", 111.12, "l1")

        # validate that the point was added.
        # other validation points are done by the influx test
        self.assertEqual(len(influx.data_points), 1)

    #happy flow - succesfully create a point
    def test_3_0_1_create_data_point_locally(self):
        # unit test pre-cleanup
        influx.clear_points()
        transform.clear_mem()  

        # add the point
        transform.create_data_point_locally("test_name", 111.12)

        # validate that the point was added.
        # other validation points are done by the influx test
        self.assertEqual(len(influx.data_points), 1)

    #happy flow - succesfully create a raw entry
    #a raw entry is a direct input of the smart meter
    def test_4_0_0_create_raw_point_locally(self):
        # unit test pre-cleanup
        influx.clear_points()
        transform.clear_mem()   

        #add the raw point
        transform.create_raw_point_locally(0, "0-0:96.7.9(00093)")

        #is the raw point present?
        self.assertEqual(len(influx.raw_data_points), 1)


    #happy flow
    def test_5_0_0_store_last_value(self):
        # unit test pre-cleanup
        influx.clear_points()
        transform.clear_mem()  

        #store a data point
        #this should create a new point in memory
        transform.store_last_value( ["e_current_consumption", None, False], 12.1 )

        #check the json scheme
        self.assertIsNotNone(transform.lastvalues)
        self.assertEqual(len(transform.lastvalues),1)
        self.assertIn("e_current_consumption", transform.lastvalues)
        self.assertIn("time", transform.lastvalues["e_current_consumption"])
        self.assertIn("value", transform.lastvalues["e_current_consumption"])
        self.assertIn("updated", transform.lastvalues["e_current_consumption"])

        #check the values
        self.assertTrue(transform.lastvalues["e_current_consumption"]["updated"])
        self.assertEqual(transform.lastvalues["e_current_consumption"]["value"], 12.1)

    #happy flow, this should clear all memory jsons
    def test_5_0_1_clear_mem(self):
        transform.clear_mem()
        self.assertEqual(len(transform.lastvalues),0)

    #happy flow
    def test_5_0_2_store_last_value(self):
        # unit test pre-cleanup
        influx.clear_points()
        transform.clear_mem()  

        #store a data point
        #this should create a new point in memory
        transform.store_last_value( ["e_volt", "l3", False], 231.1 )

        #check the json scheme
        self.assertIsNotNone(transform.lastvalues)
        self.assertEqual(len(transform.lastvalues),1)
        self.assertIn("e_volt",  transform.lastvalues)
        self.assertIn("l3", transform.lastvalues["e_volt"])
        self.assertIn("time", transform.lastvalues["e_volt"]["l3"])
        self.assertIn("value", transform.lastvalues["e_volt"]["l3"])
        self.assertIn("updated", transform.lastvalues["e_volt"]["l3"])

        #check the values
        self.assertTrue(transform.lastvalues["e_volt"]["l3"]["updated"])
        self.assertEqual(transform.lastvalues["e_volt"]["l3"]["value"],231.1)


    #happy flow
    def test_5_0_3_store_last_value(self):

        #store a data point
        #this should create a new point in memory
        transform.store_last_value( ["e_current_consumption", None, False], 12.1 )

        #check the json scheme
        self.assertIsNotNone(transform.lastvalues)
        self.assertEqual(len(transform.lastvalues),2)
        self.assertIn("e_current_consumption", transform.lastvalues)
        self.assertIn("time", transform.lastvalues["e_current_consumption"])
        self.assertIn("value", transform.lastvalues["e_current_consumption"])
        self.assertIn("updated", transform.lastvalues["e_current_consumption"])

        #check the values
        self.assertTrue(transform.lastvalues["e_current_consumption"]["updated"])
        self.assertEqual(transform.lastvalues["e_current_consumption"]["value"], 12.1)

    #happy flow, this should clear all memory jsons
    def test_5_0_5_clear_mem(self):
        transform.clear_mem()
        self.assertEqual(len(transform.lastvalues),0)


    #happy flow
    #with a first entry should return True (this was never parsed before)
    def test_6_0_0_time_to_update(self):

        #this should create a new point in memory -> True
        self.assertTrue(transform.time_to_update( ["e_current_consumption", None, False], 12.1, 10))

        #this should create a new point in memory -> True
        self.assertTrue(transform.time_to_update( ["e_volt", "l1", False], 233.1,10))

        #this should create a new point in memory -> True
        self.assertTrue(transform.time_to_update( ["e_volt", "l3", False], 231.1,10))


    #happy flow
    #should not be updated, too soon
    def test_6_0_1_time_to_update(self):

        # retry, but no update needed -> False
        self.assertFalse(transform.time_to_update( ["e_current_consumption", None, False], 12.2, 10))

        # retry, but no update needed -> False
        self.assertFalse(transform.time_to_update( ["e_volt", "l1", False], 232.0,10))

        # retry, but no update needed -> False
        self.assertFalse(transform.time_to_update( ["e_volt", "l3", False], 232.1,10))

    #happy flow
    def test_6_0_2_time_to_update(self):
        #time to update
        time.sleep(10)

        #enough time has passed -> True
        self.assertTrue(transform.time_to_update( ["e_current_consumption", None, False], 12.1, 10))

        # retry, but no update needed -> False
        self.assertTrue(transform.time_to_update( ["e_volt", "l1", False], 225.0,10))

        #enough time has passed -> True
        self.assertTrue(transform.time_to_update( ["e_volt", "l3", False], 231.1,10))

    #invalid input
    def test_6_1_0_time_to_update(self):

        #None should not be parsed and return False
        self.assertFalse(transform.time_to_update( None, 12.1, 10))


    # happy flow 
    # at startup
    def test_7_0_0_gas_flow(self):
        # unit test pre-cleanup
        influx.clear_points()
        transform.clear_mem() 

        self.assertIsNotNone(transform.transform_mem_state)
        self.assertNotIn("g_volume", transform.transform_mem_state)

    #happy flow
    # adding a first value
    def test_7_0_1_gas_flow(self):
        #this does not have a float value and should not be taken into account
        transform.gas_flow("g_blabla", "2.01")

        self.assertNotIn("g_blabla", transform.transform_mem_state)

        #no data should have been created
        self.assertEqual(len(influx.data_points), 0)

    #happy flow
    # adding a first value
    def test_7_1_0_gas_flow(self):
        transform.gas_flow("g_volume", 0.12)

        #memory should be created
        #check json scheme
        self.assertIn("g_volume", transform.transform_mem_state) 
        self.assertIn("var_value_previous", transform.transform_mem_state["g_volume"]) 
        #check value
        self.assertEqual(transform.transform_mem_state["g_volume"]["var_value_previous"], 0.12) 
           
        #no data should have been created
        self.assertEqual(len(influx.data_points), 0) 

    # happy flow
    # second value should create a data point
    def test_7_1_1_gas_flow(self):
        transform.gas_flow("g_volume", 0.23)

        #no data should have been created
        self.assertEqual(len(influx.data_points), 1) 

    def test_8_0_0_calculated_values(self):

        # unit test pre-cleanup
        influx.clear_points()
        transform.clear_mem() 

        #this should create a new point in memory -> True
        self.assertTrue(transform.time_to_update( ["e_volt", "l1", False], 231.1,10))
        self.assertTrue(transform.time_to_update( ["e_watt_consumption", "l1", False], 1.663,10))
        self.assertTrue(transform.time_to_update( ["e_watt_production", "l1", False], 0.0,10))

        #calculate the values
        transform.calculated_values()

        #no data should have been created
        self.assertEqual(len(influx.data_points), 1) 

        #validate json scheme
        self.assertIn("fields", influx.data_points[0])
        self.assertIn("e_amp_calc", influx.data_points[0]["fields"])
        self.assertEqual(7.196, influx.data_points[0]["fields"]["e_amp_calc"])

    def test_8_0_1_calculated_values(self):

        # unit test pre-cleanup
        influx.clear_points()
        transform.clear_mem() 

        #this should create a new point in memory -> True
        self.assertTrue(transform.time_to_update( ["e_volt", "l2", False], 231.1,10))
        self.assertTrue(transform.time_to_update( ["e_watt_consumption", "l2", False], 1.662,10))
        self.assertTrue(transform.time_to_update( ["e_watt_production", "l2", False], 0.0,10))

        #calculate the values
        transform.calculated_values()

        #no data should have been created
        self.assertEqual(len(influx.data_points), 1) 

        #validate json scheme
        self.assertIn("fields", influx.data_points[0])
        self.assertIn("e_amp_calc", influx.data_points[0]["fields"])
        self.assertEqual(7.192, influx.data_points[0]["fields"]["e_amp_calc"])

    def test_8_0_2_calculated_values(self):

        # unit test pre-cleanup
        influx.clear_points()
        transform.clear_mem() 

        #this should create a new point in memory -> True
        self.assertTrue(transform.time_to_update( ["e_volt", "l3", False], 231.1,10))
        self.assertTrue(transform.time_to_update( ["e_watt_consumption", "l3", False], 1.662,10))
        self.assertTrue(transform.time_to_update( ["e_watt_production", "l3", False], 0.0,10))

        #calculate the values
        transform.calculated_values()

        #no data should have been created
        self.assertEqual(len(influx.data_points), 1) 

        #validate json scheme
        self.assertIn("fields", influx.data_points[0])
        self.assertIn("e_amp_calc", influx.data_points[0]["fields"])
        self.assertEqual(7.192, influx.data_points[0]["fields"]["e_amp_calc"])

    def test_9_0_0_reset_stored(self):
        self.assertIsNone(transform.reset_stored())

if __name__ == '__main__':

    unittest.main()

