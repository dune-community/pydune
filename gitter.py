#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
(c) 2009 rene.milk@uni-muenster.de

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

B = 0.8
A = 0.1
C = 0.3

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

out = open( "simple_a.poly", 'w' )

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
out.close()