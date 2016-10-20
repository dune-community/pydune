# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 14:49:16 2012

@author: r_milk01
"""

import unittest
import os

from dune import supermodule
from dune.control import ModuleMissing, Dunecontrol

class TestControl(unittest.TestCase):

    def setUp(self):
        self.repo = supermodule.get_dune_xt_common()

    def test_control(self):
        self.assertTrue(os.path.isdir(self.repo))
        ctrl = Dunecontrol.from_basedir(self.repo)
        self.assertIn('dune-common',
                      ctrl.dependencies('dune-xt-common')['required'])
        with self.assertRaises(ModuleMissing):
            ctrl.dependencies('NONEXISTENT')
        ctrl.autogen('dune-common')
        ctrl.configure('dune-common')
        ctrl.make('dune-common')


if __name__ == '__main__':
    unittest.main()
