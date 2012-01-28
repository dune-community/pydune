#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
grammar.py (c) 2011 rene.milk@uni-muenster.de,felix.albrecht@uni-muenster.de
Licence: WTFPLv2, see LICENSE.txt
"""


import sys, math, os, time
from optparse import OptionParser

# calculate points on outer rectangle
# beginning bottom left
# rather trivial
# returns list of points in 2d
# [ [ point_x, point_y ], id_of_face_starting_clockwise_at_this_point ]
def generate_rectangle( length_x, length_y, ids ) :
	rectangle = []
	rectangle.append( [ [ 0.0, 0.0 ], ids[0] ] )
	rectangle.append( [ [ length_x, 0.0 ], ids[1] ] )
	rectangle.append( [ [ length_x, length_y ], ids[2] ] )
	rectangle.append( [ [ 0.0, length_y ], ids[3] ] )
	return rectangle

# write to trianlge
def write_to_triangle( rectangle, triangle_filename ) :
	file = open( triangle_filename, 'w' )
	# header
	file.write( '# #########################################################\n' )
	file.write( '# %s\n' %( triangle_filename ) )
	file.write( '# written by generateCube.py on %s\n' %( time.strftime('%Y/%m/%d %H:%M:%S') ) )
	total_number_of_vertices =len( rectangle )
	total_number_of_faces =len( rectangle )
	file.write( '# we have \t%i vertices\n' %( total_number_of_vertices ) )
	file.write( '#\t\t%i faces\n' %( total_number_of_faces ) )
	file.write( '#\t\t%i hole\n' %(1) )
	file.write( '# #########################################################\n' )
	file.write( '#\n' )
	# write the vertices
	file.write( '# these are the %i vertices\n' %( total_number_of_vertices ) )
	file.write( '%i 2 0 0\n' %( total_number_of_vertices ) )
	vertex_number = 0
	# and the outer rectangle
	for point_with_id_on_rectangle in rectangle :
		point_on_rectangle = point_with_id_on_rectangle[ 0 ]
		x = point_on_rectangle[ 0 ]
		y = point_on_rectangle[ 1 ]
		file.write( '\t%i\t%f\t%f\n' %( vertex_number, x, y ) )
		vertex_number += 1
	file.write( '# these were the %i vertices\n' %( total_number_of_vertices ) )
	file.write( '#\n' )
	# write the faces with boundary id
	file.write( '# these are the %i faces\n' %( total_number_of_faces ) )
	file.write( '%i 1\n' %(total_number_of_faces) )
	face_number = 0
	# of the outer rectangle
	for point_with_id_on_rectangle in rectangle :
		id = point_with_id_on_rectangle[ 1 ]
		file.write( '\t%i\t%i\t%i\t%i\n' %( face_number, face_number % len( rectangle ), ( face_number +1 ) % len( rectangle ), id ) )
		face_number += 1
	file.write( '# these were the %i faces\n' %( total_number_of_faces ) )
	file.write( '#\n' )
	# write the holes
	file.write( '# this is the hole\n' )
	file.write( '0\n' )
	# ending
	file.write( '# #########################################################\n' )
	file.write( '# end of file %s\n' %( triangle_filename ) )
	file.write( '# written by generateCube.py on %s\n' %( time.strftime('%Y/%m/%d %H:%M:%S') ) )
	file.write( '# #########################################################\n' )

## done with function definitions


def generate():
	parser = OptionParser()
	parser.add_option("-x", "--length_x", dest="length_x", default=1.,
					help="rectangle length_x", type='float')
	parser.add_option("-y", "--length_y", dest="length_y", default=1.,
					help="rectangle length_y", type='float')
	parser.add_option("-f", "--filename", dest="filename", default='cube_in_2d.poly',
					help="output filename", type='string')
	(options, args) = parser.parse_args()

	# about the outer rectangle
	rectangle_length_x = options.length_x
	rectangle_length_y = options.length_y

	# about the boundary ids
	id_of_bottom_rectangle_faces = 2
	id_of_right_rectangle_faces = 3
	id_of_top_rectangle_faces = 4
	id_of_left_rectangle_faces = 5

	# about the files to be written
	triangle_filename = options.filename

	points_on_rectangle = generate_rectangle( rectangle_length_x, rectangle_length_y, [ id_of_bottom_rectangle_faces, id_of_right_rectangle_faces, id_of_top_rectangle_faces, id_of_left_rectangle_faces ] )
	write_to_triangle( points_on_rectangle, triangle_filename )
