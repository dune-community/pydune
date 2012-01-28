#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
simple.py (c) 2010 rene.milk@uni-muenster.de
Licence: WTFPLv2, see LICENSE.txt
"""

from optparse import OptionParser

def generate():
	parser = OptionParser()
	parser.add_option("-a", "--length_a", dest="length_a", default=0.1,
					help="length_a", type='float')
	parser.add_option("-b", "--length_b", dest="length_b", default=0.7,
					help="length_b", type='float')
	parser.add_option("-c", "--length_c", dest="length_c", default=0.2,
					help="length_c", type='float')
	(options, args) = parser.parse_args()

	A = options.length_a
	B = options.length_b
	C = options.length_c

	nBids = 3

	verts = [ (0,0) , (0,A), (B-0.5*A,A), (B,A+C), (B+0.5*A,A+C) , (B,A) , (B+A,A) \
		, (B+A,0) , (B,0)  ]
	nVert = len(verts)

	bSegs = dict()
	bSegs[1] = [ (1,2), (2,3), (4,5), (5,6), (7,8), (8,0) ]
	bSegs[2] = [ (0,1) ]
	bSegs[3] = [ (3,4) ]
	bSegs[4] = [ (6,7) ]
	nBsegs = 9

	with open( "simple_a.poly", 'w' ) as out:

		out.write( '%d 2 0 %d\n'%(nVert,nBids) )
		cVert = 0
		for v in verts:
				out.write( '%d %f %f 0\n'%(cVert,v[0],v[1]) )
				cVert += 1
		out.write( '%d 1\n'%(nBsegs) )
		cBseg = 0
		for bid,vertIds in bSegs.items():
			for seg in vertIds:
				out.write( '%d %d %d %d\n'%(cBseg,seg[0],seg[1],bid)  )
				cBseg += 1

		out.write( '%d\n'%(0))
