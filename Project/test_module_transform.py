from datetime import datetime, timedelta
import time
import unittest
import sys

import module_transform as transform
import module_influx as influx

class TestStringMethods(unittest.TestCase):

    # run a number of tests on parsing
    def test_0_0_0_Dummy(self):
        self.assertEqual(True, True, "Have fun with this one, True != True")

    def test_1_0_0_Init(self):
        influx.init_influx("None", "None", "None", 8086, "None", True, True)
        transform.init_transform()
        transform.set_influx_module(influx, "smartmeter", "my_tiny_house")
        self.assertIsNotNone(transform.transform_mem_state)

    #happy flow - succesfully create a point
    def test_2_0_0_create_data_point_locally(self):
        # unit test pre-cleanup
        influx.clear_points()

        # add the point
        transform.create_data_point_locally("test_name", 111.12, "l1")

        # validate that the point was added.
        # other validation points are done by the influx test
        self.assertEqual(len(influx.data_points), 1)

    #happy flow - succesfully create a point
    def test_2_0_1_create_data_point_locally(self):
        # unit test pre-cleanup
        influx.clear_points()

        # add the point
        transform.create_data_point_locally("test_name", 111.12)

        # validate that the point was added.
        # other validation points are done by the influx test
        self.assertEqual(len(influx.data_points), 1)

    # def test_2_1_0_create_data_point_locally(self):
    #     # unit test pre-cleanup
    #     influx.clear_points()

    #     # add the point
    #     transform.create_data_point_locally(None, None)

    #     # validate that the point was added.
    #     # other validation points are done by the influx test
    #     self.assertEqual(len(influx.data_points), 0)









    # def test_3_0_0_gas_flow(self):
    #     self.assertIsNone(transform.gas_flow("gas_flow", None))
    #     self.assertIsNone(transform.gas_flow("gas_flow", '001'))
    #     self.assertNotIn("gas_flow", transform.transform_mem_state)

    # #with a first input the return should be None, but the transform_mem_state should now contain gas_flow
    # def test_3_0_1_gas_flow(self):
    #     self.assertIsNone(transform.gas_flow("gas_flow", 0.001))
    #     self.assertIn("gas_flow", transform.transform_mem_state)
    #     self.assertIn("var_value_previous", transform.transform_mem_state["gas_flow"])
        
    # # the second value will create a dif response 
    # # following values should also create a response       
    # def test_3_0_2_gas_flow(self):
    #     self.assertEqual(0.01, transform.gas_flow("gas_flow", 0.011))
    #     self.assertEqual(0.03, transform.gas_flow("gas_flow", 0.041))
    #     self.assertEqual(1.01, transform.gas_flow("gas_flow", 1.051))

    # #another var should not be created with incorrect inputs 
    # def test_3_1_0_gas_flow(self):
    #     self.assertIsNone(transform.gas_flow("gas_flow_2", None))
    #     self.assertIsNone(transform.gas_flow("gas_flow_2", '001'))
    #     self.assertNotIn("gas_flow_2", transform.transform_mem_state)

    # # create a new var in state to keep up with
    # def test_3_1_1_gas_flow(self):
    #     self.assertIsNone(transform.gas_flow("gas_flow_2", 500.001))
    #     self.assertIn("gas_flow_2", transform.transform_mem_state)
    #     self.assertIn("var_value_previous", transform.transform_mem_state["gas_flow_2"])

    # #cominning mulitple inputs
    # def test_3_1_2_gas_flow(self):
    #     self.assertEqual(0.01, transform.gas_flow("gas_flow_2", 500.011))
    #     self.assertEqual(0.03, transform.gas_flow("gas_flow_2", 500.041))
    #     self.assertEqual(2.3, transform.gas_flow("gas_flow", 3.351))
    #     self.assertEqual(1.01, transform.gas_flow("gas_flow_2", 501.051))





if __name__ == '__main__':
    unittest.main()

