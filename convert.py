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

import sys
from mesh import Mesh

usage = 'usage: %s from_filename to_filename'

def convert(from_filename,to_filename):
	m = Mesh(3)
	m.parse( from_filename )
	fn2 = m.write( to_filename )
	assert fn2 == to_filename
	
if __name__ == '__main__':
	convert( sys.argv[1], sys.argv[2] )
	try:
		convert( sys.argv[1], sys.argv[2] )

	except Exception,e:
		print 'conversion failed, ecpetion was:'
		print e
		print usage%sys.argv[0]
		