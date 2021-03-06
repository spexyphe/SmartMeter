from datetime import datetime, timedelta
import time
import unittest
import sys

import module_transform as Transform

class TestStringMethods(unittest.TestCase):

    # run a number of tests on parsing
    def test_0_0_0_Dummy(self):
        self.assertEqual(True, True, "Have fun with this one, True != True")

    def test_1_0_0_Init(self):
        
        Transform.init_transform()
        self.assertIsNotNone(Transform.transform_mem_state)


    def test_3_0_0_gas_flow(self):
        self.assertIsNone(Transform.gas_flow("gas_flow", None))
        self.assertIsNone(Transform.gas_flow("gas_flow", '001'))
        self.assertNotIn("gas_flow", Transform.transform_mem_state)

    #with a first input the return should be None, but the transform_mem_state should now contain gas_flow
    def test_3_0_1_gas_flow(self):
        self.assertIsNone(Transform.gas_flow("gas_flow", 0.001))
        self.assertIn("gas_flow", Transform.transform_mem_state)
        self.assertIn("var_value_previous", Transform.transform_mem_state["gas_flow"])
        
    # the second value will create a dif response 
    # following values should also create a response       
    def test_3_0_2_gas_flow(self):
        self.assertEqual(0.01, Transform.gas_flow("gas_flow", 0.011))
        self.assertEqual(0.03, Transform.gas_flow("gas_flow", 0.041))
        self.assertEqual(1.01, Transform.gas_flow("gas_flow", 1.051))

    #another var should not be created with incorrect inputs 
    def test_3_1_0_gas_flow(self):
        self.assertIsNone(Transform.gas_flow("gas_flow_2", None))
        self.assertIsNone(Transform.gas_flow("gas_flow_2", '001'))
        self.assertNotIn("gas_flow_2", Transform.transform_mem_state)

    # create a new var in state to keep up with
    def test_3_1_1_gas_flow(self):
        self.assertIsNone(Transform.gas_flow("gas_flow_2", 500.001))
        self.assertIn("gas_flow_2", Transform.transform_mem_state)
        self.assertIn("var_value_previous", Transform.transform_mem_state["gas_flow_2"])

    #cominning mulitple inputs
    def test_3_1_2_gas_flow(self):
        self.assertEqual(0.01, Transform.gas_flow("gas_flow_2", 500.011))
        self.assertEqual(0.03, Transform.gas_flow("gas_flow_2", 500.041))
        self.assertEqual(2.3, Transform.gas_flow("gas_flow", 3.351))
        self.assertEqual(1.01, Transform.gas_flow("gas_flow_2", 501.051))





if __name__ == '__main__':
    unittest.main()

