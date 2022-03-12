from datetime import datetime, timedelta
import time
import unittest

import sys
from pathlib import Path

from pip import main

file = Path(__file__).resolve()
parent, top = file.parent, file.parents[3]

sys.path.append(str(top))

try:
    sys.path.remove(str(parent))
except ValueError: # Already removed
    pass

import Project.test.unit
__package__ = 'Project.test.unit'

from ... import main_smart_meter as meter


class TestStringMethods(unittest.TestCase):

                                                                                                                        
    def test_dummy(self):
        self.assertEqual(True, True)

if __name__ == '__main__':

    unittest.main()

