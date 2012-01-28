# Copyright (C) 2010 Tobi Vollebregt

import os
import unittest
import tempfile
import shutil
import filecmp
from dune.mesh import Mesh

class TestConvert(unittest.TestCase):
	grid_dir = os.path.join(os.path.dirname(__file__),"files")

	def setUp(self):
		self.tmpdir = tempfile.mkdtemp()
		print(self.tmpdir)

	def tearDown(self):
		#shutil.rmtree(self.tmpdir)
		pass

	def test_same(self):
		m1 = Mesh(3)
		infile_name = "2d.smesh"
		infile_path = os.path.join(self.grid_dir,infile_name)
		m1.parse( infile_path )
		outfile_path = os.path.join(self.tmpdir,infile_name)
		fn2 = m1.write(outfile_path)
		self.assertEqual(fn2, outfile_path)
		m2 = Mesh(3)
		m2.parse(outfile_path)
		are_same = m2.equals(m1)
		if not are_same:
			import difflib
			diff = difflib.HtmlDiff().make_file( 
				open(infile_path).readlines(), 
				open(outfile_path).readlines() )
			open( os.path.join( self.tmpdir, '%s.diff.html'%infile_name ) ,'w' ).writelines(diff)
		self.assertTrue(are_same)			

if __name__ == '__main__':
	unittest.main()