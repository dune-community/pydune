#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
randomized.py (c) 2010 rene.milk@uni-muenster.de
Licence: WTFPLv2, see LICENSE.txt
"""


import matplotlib as ml
import matplotlib.pyplot as pp
import matplotlib.delaunay
import random

class RandomGrid( ml.delaunay.triangulate.Triangulation ):
	def __init__( self, num_inserted=4,random_func=random.uniform ):
		min_x = -1
		max_x = 1
		min_y = -1
		max_y = 1
		x = [min_x,min_x,max_x,max_x]
		y = [min_y,max_y,max_y,min_y]
		x.extend( random_func(min_x,max_x) for i in range(num_inserted) )
		y.extend( random_func(min_y,max_y) for i in range(num_inserted) )
		super(RandomGrid,self).__init__( x, y )
		self.xtris = [ [self.x[node[i]] for i in range(3) ] for node in self.triangle_nodes]
		self.ytris = [ [self.y[node[i]] for i in range(3) ] for node in self.triangle_nodes]
       
	def toSmesh(self,filename):
		with open( filename, 'wb' ) as f:
			f.write( '%d 2 0 %d\n'%(len(self.x),1) )
			vert_count = 0
			for x,y in zip(self.x,self.y):
				f.write( '%d %f %f 0\n'%(vert_count,x,y ) )
				vert_count += 1
			f.write( '%d 1\n'%(len(self.triangle_nodes)*3) )            
			line_count = 0
			bid = 1
			for node in self.triangle_nodes:
				f.write( '%d %d %d %d\n'%(line_count,node[0],node[1],bid)  )
				line_count += 1
				f.write( '%d %d %d %d\n'%(line_count,node[1],node[2],bid)  )
				line_count += 1
				f.write( '%d %d %d %d\n'%(line_count,node[2],node[0],bid)  )
				line_count += 1
			f.write( '%d\n'%(0))
			
	def toDGF(self,filename):
		with open( filename, 'wb' ) as f:
			f.write( 'DGF\nVERTEX\n' )
			for x,y in zip(self.x,self.y):
				f.write( '%f %f\n'%(x,y ) )
			f.write( '#\nSIMPLEX\n' )            
			line_count = 0
			for node in self.triangle_nodes:
				f.write( '%d %d %d\n'%(node[0],node[1],node[2])  )
			f.write( 'BOUNDARYDOMAIN\ndefault 5\n#\n')
            
	def tris(self):
		return self.xtris,self.ytris

from optparse import OptionParser

def generate():
	## global defines
	parser = OptionParser()
	parser.add_option("-p", "--points", dest="points", default=100,
					help="points", type='int')
	parser.add_option("-f", "--filename", dest="filename", default="random",
					help="filename", type='string')
	parser.add_option("-c", "--length_c", dest="length_c", default=0.2,
					help="length_c", type='float')
	(options, args) = parser.parse_args()

	if False:
		import matplotlib.gridspec as gridspec
		gs = gridspec.GridSpec(1, 4,width_ratios=[1,1])
		pp.figure(figsize=(12, 12))
		for i in range(4):
			grid = RandomGrid(  )
			#grid.toSmesh("m.smesh")
			xtris,ytris = grid.tris()
			#pp.subplot(1,3,i)
			pp.subplot(gs[0,i])
			for xtips,ytips in zip(xtris,ytris):
				pp.fill(xtips,ytips,facecolor='r',edgecolor='b')
		pp.title('Sequential Plotting')
		pp.show()
	else:
		grid = RandomGrid( options.points, random.triangular )
		grid.toDGF("%s.dgf"%options.filename)
		grid.toSmesh("%s.poly"%options.filename)
		#pp.figure(figsize=(12, 12))
		#xtris,ytris = grid.tris()
		#for xtips,ytips in zip(xtris,ytris):
			#pp.fill(xtips,ytips,facecolor='r',edgecolor='b')
		#pp.show()
