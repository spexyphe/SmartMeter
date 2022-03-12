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


if __name__ == '__main__':

    unittest.main()

