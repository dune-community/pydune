# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 14:00:46 2012

@author: r_milk01
"""

import unittest
import os

from dune import supermodule

class TestSuper(unittest.TestCase):


    def test_create(self):
        stuff_dir = supermodule.get_dune_stuff()
        self.assertFalse(os.path.isdir(stuff_dir))


if __name__ == '__main__':
    unittest.main()