#!/usr/bin/python
# -*- coding: utf-8 -*-

from gridhelper import *
from functors import *
from optparse import OptionParser
import math, copy

parser = OptionParser()
parser.add_option("-a", "--area", dest="area", default=math.pi,
                  help="area of boundary", type='float')

parser.add_option("-l", "--length", dest="tube_length", default=10,
                  help="tube length", type='float')

parser.add_option("-y", "--hyp_fac", dest="hyp_fac", default=4.,
                  help="hyperbole factor", type='float')

parser.add_option("-d", "--hyp_add", dest="hyp_add", default=1.,
                  help="hyperbole additive", type='float')

parser.add_option("-n", "--num_verts", dest="num_verts", default=6,
                  help="number of vertices in circle approx", type='int')

parser.add_option("-m", "--num_midrings", dest="num_midrings", default=0,
                  help="number midrings inserted between boundary faces", type='int')

parser.add_option("-f", "--filename", dest="filename", default='out.smesh',
                  help="output filename", type='string')

(options, args) = parser.parse_args()

area 			= options.area
tube_length		= options.tube_length
num_verts 		= options.num_verts
alpha			= math.radians( 360. / (num_verts ) )
alpha_half		= alpha / 2.
num_midrings	= int(options.num_midrings)
area_one_tri = math.pi / float(num_verts)
L_x = math.sqrt( area_one_tri / ( math.sin( alpha_half ) * math.cos( alpha_half ) ) )
functor = HyperboleFunctorZ(tube_length, options.hyp_fac, options.hyp_add )

"""left boundary area"""
origin_L = Vector3(0,0,0)
points_L = PLCPointList( 3 )
bound_L = FanningSimplexList( points_L.appendVert( origin_L ), 2 )
L = functor.scale( Vector3( L_x, 0, 0 ) )
bound_L.addVertex( points_L.appendVert( L ) )
rot_mat = Matrix4.new_rotatez( alpha )
for i in range( 1, num_verts  ):
	L = rot_mat * L
	bound_L.addVertex(points_L.appendVert( L ))
bound_L.close()
grid = FullGrid( bound_L, 4 )

""" midrings, if num > 0 """
incr = tube_length / float( num_midrings + 1 )
for i in range( 1, num_midrings + 1 ):
	points_M = PLCPointList( 3 )
	bound_M = InbetweenRing( )
	M = functor.scale( Vector3( L_x, 0, incr*float(i) ) )
	bound_M.addVertex( points_M.appendVert( M ) )
	for i in range( 1, num_verts  ):
		M = rot_mat  * M
		bound_M.addVertex(points_M.appendVert( M ))
	grid.connect(bound_M)

"""right boundary"""
kipp_mat = Matrix4.new_rotatey( math.radians(15) )
origin_R = Vector3(0,0,tube_length )
points_R = PLCPointList( 3 )
bound_R = FanningSimplexList( points_R.appendVert( origin_R ), 3 )
R = functor.scale( Vector3( L_x, 0, tube_length ) )
#R = kipp_mat * R #skalier groesser R
bound_R.addVertex( points_R.appendVert( R ) )
for i in range( 1, num_verts  ):
	R = rot_mat  * R
	bound_R.addVertex(points_R.appendVert( R ))
bound_R.close()

grid.connect(bound_R)
grid.outputPLC( options.filename )
