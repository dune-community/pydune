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

import sys,difflib
from mesh import Mesh
from tempfile import NamedTemporaryFile

def parseWriteDiff(filename):
	m = Mesh(3)
	m.parse( filename )
	t = NamedTemporaryFile(suffix=filename[filename.rindex('.'):])
	fn2 = m.write( t.name )
	#diff = difflib.unified_diff( open( filename ).readlines(), open( fn2 ).readlines() )
	diff = difflib.HtmlDiff().make_file( open( filename ).readlines(), open( fn2 ).readlines() )
	open( '%s.diff.html'%filename ,'w' ).writelines(diff)
	m.parse( fn2 )

def convertDiff(filename):
	m = Mesh(3)
	sf = filename[filename.rindex('.'):]
	if sf == '.smesh':
		sf_o = '.ply'
	else:
		sf_o = '.smesh'
	m.parse( filename )
	t = NamedTemporaryFile(suffix=sf_o)
	m.write( t.name )
	m.parse( t.name )
	t2 = NamedTemporaryFile(suffix=sf)
	fn2 = m.write( t2.name )
	#diff = difflib.unified_diff( open( filename ).readlines(), open( fn2 ).readlines() )
	diff = difflib.HtmlDiff().make_file( open( filename ).readlines(), open( fn2 ).readlines() )
	open( '%s.convert.diff.html'%filename ,'w' ).writelines(diff)

if __name__ == '__main__':
	for fn in ['test_grids/tube.smesh', 'test_grids/aorta_dune.smesh' ]:
		print 'testing %s '%fn, '-'*50
		print '-'*10 , 'parseWriteDiff'
		parseWriteDiff( fn )
		print '-'*10 , 'convertDiff'
		convertDiff( fn )