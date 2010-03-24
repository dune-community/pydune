#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gridhelper.py (c) 2009 rene.milk@uni-muenster.de

It is licensed to you under the terms of the WTFPLv2 (see below).

This program is free software. It comes with no warranty,
to the extent permitted by applicable law.


            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                    Version 2, December 2004

 Copyright (C) 2004 Sam Hocevar
  14 rue de Plaisance, 75014 Paris, France
 Everyone is permitted to copy and distribute verbatim or modified
 copies of this license document, and changing it is allowed as long
 as the name is changed.

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. You just DO WHAT THE FUCK YOU WANT TO.
"""

import sys,difflib,traceback
from mesh import Mesh
from tempfile import NamedTemporaryFile
from PyQt4 import QtGui
from viewer import MeshViewer

def parseWriteDiff(filename,do_diff=False):
	m = Mesh(3)
	m.parse( filename )
	t = NamedTemporaryFile(suffix=filename[filename.rindex('.'):])
	fn2 = m.write( t.name )
	#diff = difflib.unified_diff( open( filename ).readlines(), open( fn2 ).readlines() )
	if do_diff:
		print '-'*15 , 'generating diff output, parseWriteDiff'
		diff = difflib.HtmlDiff().make_file( open( filename ).readlines(), open( fn2 ).readlines() )
		open( '%s.diff.html'%filename ,'w' ).writelines(diff)

def convertDiff(filename,do_diff=False):
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
	except Exception, e:
		t.seek(0)
		open( '/tmp/error.log', 'w').writelines( t.readlines() )
		print traceback.format_exc()
		raise e
	#diff = difflib.unified_diff( open( filename ).readlines(), open( fn2 ).readlines() )
	if do_diff:
		print '-'*15 , 'generating diff output, convertDiff'
		diff = difflib.HtmlDiff().make_file( open( filename ).readlines(), open( fn2 ).readlines() )
		open( '%s.convert.diff.html'%filename ,'w' ).writelines(diff)

def viewerTest(filename):
	app = QtGui.QApplication(['MeshViewer'])
	window = MeshViewer(filename)
	window.show()
	#app.exec_()

if __name__ == '__main__':
	do_diff = False
	if len(sys.argv) > 1:
		grids = sys.argv[1:]
	else:
		grids = ['test_grids/colored_aorta.ply','test_grids/tube.smesh', 'test_grids/aorta_dune.smesh' ]
	for fn in grids:
		print '-'*5, 'testing %s '%fn
		print '-'*10 , 'parseWriteDiff'
		parseWriteDiff( fn, do_diff )
		print '-'*10 , 'convertDiff'
		convertDiff( fn, do_diff )
		print '-'*10 , 'viewerTest'
		viewerTest(fn)