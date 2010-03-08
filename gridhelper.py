#!/usr/env/python
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

class DimensionIncompatibleException(Exception):
	pass

class ImpossibleException(Exception):
	pass

import math, copy
from euclid import *

class PLCPointList:
	"""static var numbering all vertices"""
	global_vertices = []

	def __init__(self, dim ):
		self.dim = dim
		self.verts = dict()

	def appendVert(self,x):
		if not x in PLCPointList.global_vertices:
			PLCPointList.global_vertices.append(x)
			glob_idx = len(PLCPointList.global_vertices)
		else:
			glob_idx = PLCPointList.global_vertices.index(x)
		self.verts[glob_idx] = x
		assert isinstance( glob_idx, int )
		return glob_idx

	def simpleString(self):
		ret = ''
		for idx,p in self.verts.iteritems():
			ret += 'Vertix %4d \t%s\n'% (idx,str(p))
		return ret

	def __len__(self):
		return len(self.verts)

class Simplex:
	def __init__(self,v1,v2,v3):
		assert isinstance( v1, int )
		self.v1 = v1
		assert isinstance( v2, int )
		self.v2 = v2
		assert isinstance( v3, int )
		self.v3 = v3

	def __repr__(self):
		return 'Simplex (%4d,%4d,%4d)'%(self.v1,self.v2,self.v3)

class FanningSimplexList:
	def __init__(self,center_idx,bid):
		self.center_idx = center_idx
		self.simplices 	= []
		self.boundaryId = bid
		self.vertex_idx = []

	def addVertex(self,v_idx):
		self.vertex_idx.append( v_idx )
		if len(self.vertex_idx) > 1:
			self.simplices.append( Simplex( self.center_idx, self.vertex_idx[-1], self.vertex_idx[-2]  ) )

	def close(self):
		"""finish last simplex"""
		self.simplices.append( Simplex( self.center_idx, self.vertex_idx[-1], self.vertex_idx[0]  ) )

	def __repr__(self):
		ret = 'FanningSimplexList  for boundary ID %d\n'%(self.boundaryId)
		i = 0
		for s in self.simplices:
			ret += '%4d %s\n'%(i,s)
			i += 1
		return ret

	def __str__(self):
		return self.__repr__()

class InbetweenRing:
	def __init__(self):
		self.vertex_idx = []

	def addVertex(self,v_idx):
		self.vertex_idx.append( v_idx )

	def __repr__(self):
		ret = 'InbetweenRing \n'
		i = 0
		for s in self.vertex_idx:
			ret += 'Vertex %4d %s\n'%(i,s)
			i += 1
		return ret

	def __str__(self):
		return self.__repr__()


class FullGrid:
	def __init__(self,f1,default_Bid):
		self.fans 					= [f1]
		self.default_Bid 			= default_Bid
		self.connecting_simplices 	= []
		self.rings					= []

	def connect(self,new_f):
		f1 = f2 = None
		if isinstance( new_f, InbetweenRing ):
			print 'connecting InbetweenRing\n'
			self.rings.append( new_f )
			if len(self.rings) > 1:
				f1 = self.rings[-2]
			else:
				f1 = self.fans[-1]
		elif isinstance( new_f, BoundarySurface ):
			print 'connecting BoundarySurface\n'
			self.fans.append( new_f )
			if len(self.rings) > 0:
				f1 = self.rings[-1]
			else:
				f1 = self.fans[-2]
		f2 = new_f
		if len(f1.vertex_idx) !=  len(f2.vertex_idx):
			raise DimensionIncompatibleException()
		b_len = len(f1.vertex_idx)
		for i in range ( 0, b_len  ):
			self.connecting_simplices.append( \
				Simplex(	f1.vertex_idx[i-1],
							f2.vertex_idx[i-1], \
							f1.vertex_idx[i] ) )
			self.connecting_simplices.append( \
				Simplex(	f1.vertex_idx[i],
							f2.vertex_idx[i], \
							f2.vertex_idx[i-1] ) )
	def __str__(self):
		ret = 25*'=' + 'GRID'+ 25*'=' + '\nconnecting simplices %d\n'%(len(self.connecting_simplices))
		for s in self.connecting_simplices:
			ret += str(s) + '\n'
		ret += 'FanningSimplexLists:\n'
		for f in self.fans:
			ret += str(f) + '\n'
		ret += 'InbetweenRings:\n'
		for r in self.rings:
			ret += str(r) + '\n'
		ret += 25*'=' + 'GRID'+ 25*'='
		return ret

	def outputPLC(self, fn, args, options ):
		out = None
		if not fn.endswith( '.smesh' ):
			fn += '.smesh'
		try:
			out = open(fn,'w')
		except:
			raise ImpossibleException()
		out.write( '# commandline: %s\n'%' '.join( args ) )
		out.write( '# options: %s\n'%options )
		out.write( '%d 3 0 %d\n'%(len(PLCPointList.global_vertices),3) )#3 bids
		cVert = 1
		for v in PLCPointList.global_vertices:
				out.write( '%d %f %f %f\n'%(cVert,v.x,v.y,v.z) )
				cVert += 1
		boundary_segment_count = len(self.connecting_simplices)
		for f in self.fans:
			boundary_segment_count += len(f.simplices)
		out.write( '%d 1\n'%(boundary_segment_count) )
		cBseg = 0
		for f in self.fans:
			assert isinstance( f, BoundarySurface )
			for b1 in f.simplices:
				assert isinstance( b1, Simplex )
				out.write( '%d %d %d %d %d\n'%(3,b1.v1,b1.v2,b1.v3,f.boundaryId)  )
				cBseg += 1
		for c in self.connecting_simplices:
			out.write( '%d %d %d %d %d\n'%(3,c.v1,c.v2,c.v3,self.default_Bid)  )
			cBseg += 1
		out.write( '%d\n'%(0))

class BoundarySurface:
	def __init__(self, mid, first, count_inner_rings, count_spokes, bid ):
		self.mid 				= mid
		self.first 				= first
		self.count_inner_rings 	= count_inner_rings
		self.count_spokes 		= count_spokes
		self.boundaryId 		= bid
		self.alpha				= math.radians( 360. / (self.count_spokes ) )
		self.alpha_half			= self.alpha / 2.0

		self.simplices				= []	
		self.outer_vertices_idx 	= []
		self.inner_vertices_idx 	= []
		self.vertices 				= PLCPointList( 3 )
		self.spokes					= []
		self.mid_idx 				= self.vertices.appendVert( self.mid )
		
		rot_mat = Matrix4.new_rotatez( self.alpha )
		
		L = Vector3(self.first.x, self.first.y, self.first.z)
		z_offset = Vector3(0, 0, self.first.z)
		for i in range( 0, self.count_spokes  ):
			if i != 0:
				L -= z_offset
				L = rot_mat * L
				L += z_offset
			L_idx = self.vertices.appendVert( L )
			self.outer_vertices_idx.append( L_idx )
			spoke_direction = self.mid - L 
			assert self.mid.z == L.z
			spoke_vertex_idx = []
			spoke_vertex_idx.append( L_idx )
			spoke_add  = spoke_direction / float( self.count_inner_rings )
			for i in range( 1, self.count_inner_rings ):
				p = L + ( i * spoke_add )
				spoke_vertex_idx.append( self.vertices.appendVert( p ) )
			self.inner_vertices_idx.append( spoke_vertex_idx[-1] )
			self.spokes.append( spoke_vertex_idx )

		for i in range( 0, self.count_spokes ):
			current_spoke = self.spokes[i-1]
			left_spoke = self.spokes[i-2]
			right_spoke = self.spokes[i]
			for j in range( 0, self.count_inner_rings - 1 ):
				#print 'current spoke j,j+1, left spoke j: %f - %f - %f '%(current_spoke[j], current_spoke[j+1], left_spoke[j])
				self.simplices.append( Simplex( current_spoke[j], current_spoke[j+1], left_spoke[j] ) )
				self.simplices.append( Simplex( current_spoke[j], current_spoke[j+1], right_spoke[j+1] ) )

		for i in range( 0, len(self.inner_vertices_idx)  ):
			self.simplices.append( Simplex( self.inner_vertices_idx[i], self.inner_vertices_idx[i-1], self.mid_idx ) )

		#this is exposed to FullGrid
		self.vertex_idx = self.outer_vertices_idx

class Simplex3:
	def __init__(self,a,b,c,pl):
		assert isinstance(pl,PLCPointList)
		assert isinstance(a,int)
		assert isinstance(b,int)
		assert isinstance(c,int)
		assert a!=b and b !=c and b!=c
		self.idx = ( a,b,c )
		self.edge_idx = ( (a,b), (b,c), (c,a) )
		self.reset(pl)
		
	def reset(self,pl):
		self.v = []
		for id in self.idx:
			self.v.append( pl.verts[id] )
		self.n = (self.v[0] + self.v[1]).cross(self.v[0] + self.v[2])
		self.edges = ( self.v[1] - self.v[0], self.v[2] - self.v[1], self.v[0] - self.v[2] )

	def __repr__(self):
		return 'simplex (%d,%d,%d) -- (%s,%s,%s)'%(self.idx[0],self.idx[1],self.idx[2],self.v[0],self.v[1],self.v[2])

class Simplex2:
	def __init__(self,a,b,pl):
		assert isinstance(pl,PLCPointList)
		assert isinstance(a,int)
		assert isinstance(b,int)
		self.idx = ( a, b)
		self.reset(pl)
		
	def reset(self,pl):
		self.v = []
		for id in self.idx:
			self.v.append( pl.verts[id] )
		self.n = (self.v[0]).cross(self.v[1])
		
def simplex(pl,a,b,c=None):
	if c:
		return Simplex3(a,b,c,pl)
	else:
		return Simplex2(a,b,pl)
		
def vector( x,y,z=None ):
	if z:
		return Vector3( float(x),float(y),float(z) )
	else:
		return Vector2( float(x),float(y) )



