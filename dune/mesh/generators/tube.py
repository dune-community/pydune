#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tube.py (c) 2010 rene.milk@uni-muenster.de
Licence: WTFPLv2, see LICENSE.txt
"""

from dune.mesh.util.gridhelper import *
from _functors import *
from optparse import OptionParser
import math, copy, sys
from dune.mesh.util.meshutil import BoundaryIdToColorMapper

use_hyperbole_functor = False
def functor_callback(option, opt_str, value, parser):
	global use_hyperbole_functor
	setattr(parser.values, option.dest, 1)
	use_hyperbole_functor = True

def generate():
	global use_hyperbole_functor
	parser = OptionParser()
	parser.add_option("-a", "--area", dest="area", default=math.pi,
					help="area of boundary", type='float')

	parser.add_option("-l", "--length", dest="tube_length", default=10,
					help="tube length", type='float')

	parser.add_option("-y", "--hyp_fac", dest="hyp_fac", default=4.,
					help="hyperbole factor", type='float',
					action='callback',callback=functor_callback )

	parser.add_option("-d", "--hyp_add", dest="hyp_add", default=1.,
					help="hyperbole additive", type='float',
					action='callback',callback=functor_callback )

	parser.add_option("-n", "--num_verts", dest="num_verts", default=6,
					help="number of vertices in circle approx", type='int')

	parser.add_option("-m", "--num_midrings", dest="num_midrings", default=0,
					help="number of midrings inserted between boundary faces", type='int')

	parser.add_option("-s", "--num_spoke_points", dest="num_spoke_points", default=2,
					help="number of spoke points on boundary faces", type='int')

	parser.add_option("-f", "--filename", dest="filename", default='out.smesh',
					help="output filename", type='string')

	(options, args) = parser.parse_args()

	area 			= options.area
	tube_length		= options.tube_length
	num_verts 		= options.num_verts
	alpha			= math.radians( 360. / (num_verts ) )
	alpha_half		= alpha / 2.0
	num_midrings	= int(options.num_midrings)
	num_spoke_points = options.num_spoke_points
	assert num_spoke_points > 0
	area_one_tri = area * math.pi / float(num_verts)
	L_x = math.sqrt( area_one_tri / ( math.sin( alpha_half ) * math.cos( alpha_half ) ) )
	if use_hyperbole_functor:
		functor = HyperboleFunctorZ(tube_length, options.hyp_fac, options.hyp_add )
		print "using hyperbole functor"
	else:
		functor = IdentityFunctor()
		print "using identity functor"

	bidMapper = BoundaryIdToColorMapper(5)
	"""left boundary area"""

	origin_L = Vector3(0,0,0)
	L = functor.scale( Vector3( L_x, 0, 0 ) )
	bound_L = BoundarySurface( bidMapper, origin_L, L, num_spoke_points, num_verts, 2 )

	grid = FullGrid( bound_L, 4 )

	""" midrings, if num > 0 """
	rot_mat = Matrix4.new_rotatez( alpha )
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
	R = functor.scale( Vector3( L_x, 0, tube_length ) )
	bound_R = BoundarySurface( bidMapper, origin_R, R, num_spoke_points, num_verts, 3, True )

	grid.connect(bound_R)
	grid.outputPLC( options.filename, sys.argv, options )
