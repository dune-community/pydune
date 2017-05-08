# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 13:33:33 2012

@author: r_milk01
"""


import difflib
import traceback
from dune.mesh import Mesh
from tempfile import NamedTemporaryFile
import unittest
from os.path import (join, dirname, abspath)

def _parseWriteDiff(filename,do_diff=False):
    m = Mesh(3)
    m.parse( filename )
    t = NamedTemporaryFile(suffix=filename[filename.rindex('.'):])
    fn2 = m.write( t.name )
    #diff = difflib.unified_diff( open( filename ).readlines(), open( fn2 ).readlines() )
    if do_diff:
        print(('-'*15 , 'generating diff output, parseWriteDiff'))
        diff = difflib.HtmlDiff().make_file( open( filename ).readlines(), open( fn2 ).readlines() )
        open( '%s.diff.html'%filename ,'w' ).writelines(diff)


def _convertDiff(filename,do_diff=False):
    m = Mesh(3)
    sf = filename[filename.rindex('.'):]
    if sf == '.smesh':
        sf_o = '.ply'
    else:
        sf_o = '.smesh'
    try:
        m.parse( filename )
        t = NamedTemporaryFile(suffix=sf_o)
        m.write( t.name )
        m.parse( t.name )
        t2 = NamedTemporaryFile(suffix=sf)
        fn2 = m.write( t2.name )
    except Exception as e:
        t.seek(0)
        open( '/tmp/error.log', 'w').writelines( t.readlines() )
        print((traceback.format_exc()))
        raise e
    #diff = difflib.unified_diff( open( filename ).readlines(), open( fn2 ).readlines() )
    if do_diff:
        print('-'*15 , 'generating diff output, convertDiff')
        diff = difflib.HtmlDiff().make_file( open( filename ).readlines(), open( fn2 ).readlines() )
        open( '%s.convert.diff.html'%filename ,'w' ).writelines(diff)

class TestDiffs(unittest.TestCase):
    fn = ['colored_aorta.ply', 'tube.smesh', 'aorta_dune.smesh' ]
    grids = [ join(dirname(abspath(__file__)), 'files/', j) for j in fn]


    def test_same(self):
        do_diff = True
        for grid in self.grids:
            yield _parseWriteDiff, grid, do_diff
            yield _convertDiff, grid, do_diff


if __name__ == '__main__':
    unittest.main()