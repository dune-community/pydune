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
import utils

def find_key(dic, val):
	"""return the key of dictionary dic given the value"""
	return [k for k, v in dic.iteritems() if v == val][0]

class ColorToBoundaryIdMapper:
	def __init__(self):
		self.known_colors = []

	def getID(self, color):
		assert isinstance( color, Vector3 )
		if not color in self.known_colors:
			self.known_colors.append(color)
		return self.known_colors.index(color) + 1

class BoundaryIdToColorMapper:
	def __init__(self,expected=11):
		self.bids = []
		self.expected = expected
		self.colormap = utils.getColourPaletteCheat(expected,[(0.0,0,0.0)])
       
	def getColor(self, bid):
		if not bid in self.bids:
			self.bids.append(bid)
		try:
			c = self.colormap[ self.bids.index(bid) ]
			return Vector3( c[0], c[1], c[2] )
		except Exception, e:
			print e
			print bid
			return Vector3()

class PLCPointList:
	"""static var numbering all vertices"""
	global_vertices = []

	def __init__(self, dim ):
		self.dim = dim
		self.verts = dict()
		self.attribs = dict()
		#set to -1 so we get a 0-based index for verts dict
		self.duplicate_count = -1
		#alias -> real vertex id mapping
		self.aliases = dict()
		self.duplicates = []

	def appendVert(self,x,c):
		assert isinstance( c, Vector3 )
		glob_idx = len(PLCPointList.global_vertices) + len(self.aliases) 
		if not x in PLCPointList.global_vertices:
			PLCPointList.global_vertices.append(x)
		else:
			assert x not in self.duplicates
			self.duplicates.append( x )
			x_id = find_key(self.verts, x)
			self.aliases[glob_idx] = x_id
			assert self.verts[x_id] == x, '%d -- %d | %s -- %s'%(glob_idx,x_id, x, self.verts[x_id] )
		
		self.verts[glob_idx] = x
		self.attribs[glob_idx] = c
		return glob_idx

	def simpleString(self):
		ret = ''
		for idx,p in self.verts.iteritems():
			ret += 'Vertix %4d \t%s\n'% (idx,str(p))
		return ret

	def __len__(self):
		return len(self.verts)

	def unalias(self,idx):
		if self.aliases.has_key(idx):
			return self.aliases[idx]
		else:
			return idx

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
				Simplex(	f1.vertex_idx[i],
							f2.vertex_idx[i-1], \
							f1.vertex_idx[i-1] ) )
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
		out.write( '# all vertices\n#\n' )
		cVert = 0
		for v in PLCPointList.global_vertices:
				out.write( '%d %f %f %f\n'%(cVert,v.x,v.y,v.z) )
				cVert += 1
		boundary_segment_count = len(self.connecting_simplices)
		for f in self.fans:
			boundary_segment_count += len(f.simplices)
		out.write( '\n# number of facets (= number of triangles), border marker\n#\n%d 1\n'%(boundary_segment_count) )
		out.write( '# all faces\n#\n' )
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
	def __init__(self, bidMapper, mid, first, count_inner_rings, count_spokes, bid, flip_face_def=False ):
		self.color				= bidMapper.getColor(bid)
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
		self.mid_idx 				= self.vertices.appendVert( self.mid, self.color )
		
		rot_mat = Matrix4.new_rotatez( self.alpha )
		
		L = Vector3(self.first.x, self.first.y, self.first.z)
		z_offset = Vector3(0, 0, self.first.z)
		for i in range( 0, self.count_spokes  ):
			if i != 0:
				L -= z_offset
				L = rot_mat * L
				L += z_offset
			L_idx = self.vertices.appendVert( L, self.color )
			self.outer_vertices_idx.append( L_idx )
			spoke_direction = self.mid - L 
			assert self.mid.z == L.z
			spoke_vertex_idx = []
			spoke_vertex_idx.append( L_idx )
			spoke_add  = spoke_direction / float( self.count_inner_rings )
			for i in range( 1, self.count_inner_rings ):
				p = L + ( i * spoke_add )
				spoke_vertex_idx.append( self.vertices.appendVert( p, self.color ) )
			self.inner_vertices_idx.append( spoke_vertex_idx[-1] )
			self.spokes.append( spoke_vertex_idx )

		for i in range( 0, self.count_spokes ):
			current_spoke = self.spokes[i-1]
			left_spoke = self.spokes[i-2]
			right_spoke = self.spokes[i]
			for j in range( 0, self.count_inner_rings - 1 ):
				#print 'current spoke j,j+1, left spoke j: %f - %f - %f '%(current_spoke[j], current_spoke[j+1], left_spoke[j])
				if flip_face_def:
					self.simplices.append( Simplex( current_spoke[j], current_spoke[j+1], left_spoke[j]  ) )
					self.simplices.append( Simplex( right_spoke[j+1], current_spoke[j+1], current_spoke[j] ) )
				else:
					self.simplices.append( Simplex( left_spoke[j], current_spoke[j+1], current_spoke[j] ) )
					self.simplices.append( Simplex( current_spoke[j], current_spoke[j+1], right_spoke[j+1] ) )

		for i in range( 0, len(self.inner_vertices_idx)  ):
			if flip_face_def:
				self.simplices.append( Simplex( self.inner_vertices_idx[i-1], self.inner_vertices_idx[i], self.mid_idx ) )
			else:
				self.simplices.append( Simplex( self.mid_idx, self.inner_vertices_idx[i],self.inner_vertices_idx[i-1] ) )

		#this is exposed to FullGrid
		self.vertex_idx = self.outer_vertices_idx

class Simplex3:
	def __init__(self,a,b,c,pl,f_id,color=None):
		assert isinstance(pl,PLCPointList)
		assert isinstance(a,int)
		assert isinstance(b,int)
		assert isinstance(c,int)
		assert a!=b and b !=c and b!=c, 'degenerated simplex'
		assert a > -1, 'negative vertex id: %d / %d / %d'%(a,b,c)
		assert b > -1, 'negative vertex id: %d / %d / %d'%(a,b,c)
		assert c > -1, 'negative vertex id: %d / %d / %d'%(a,b,c)
		self.attribs = ( pl.attribs[a], pl.attribs[b], pl.attribs[c] )
		#use the real ids for drawing and morphing stuff
		oa = a
		ob = b
		oc = c
		a = pl.unalias(a)
		b = pl.unalias(b)
		c = pl.unalias(c)
		self.idx = ( a,b,c )
		ok = []
		if oa != a or ob != b or oc != c:
			for id in ( (a,oa) ,(b,ob),(c,oc)):
				assert pl.verts[id[0]] == pl.verts[id[1]] , '%s%s%s -- %s\n%s'%(pl.verts[id[0]], ' -- ', pl.verts[id[1]], id, ok)
				ok.append( id )
		self.edge_idx = ( (a,b), (b,c), (c,a) )
		self.id = f_id
		self.reset(pl)
		self.m = Vector3()
		if color != None:
			self.color = color
		else:
			self.color = self.attribs[0]/255.0
		
	def reset(self,pl):
		self.v = []
		self.center = Vector3()
		for id in self.idx:
			self.v.append( pl.verts[id] )
			self.center += pl.verts[id]
		self.center /= 3.0
		if self.v[0] < self.v[1]  and self.v[1] < self.v[2]:
			self.n = ( - self.v[0] + self.v[1] ).cross( - self.v[0] + self.v[2] )
			#elif self.v[0] < self.v[1]  and self.v[1] > self.v[2]:
				#self.n = (self.v[0] - self.v[1] ).cross(   self.v[1] - self.v[2] ) * -1
		else:
			self.n = (self.v[0] - self.v[1] ).cross(   self.v[1] - self.v[2] ) 
		n_abs = abs(self.n)
		if n_abs != 0.0:
			self.n /= n_abs
		self.edges = ( self.v[1] - self.v[0], self.v[2] - self.v[1], self.v[0] - self.v[2] )
		self.area  = n_abs * 0.5

	def __repr__(self):
		return 'simplex (%d,%d,%d) -- (%s,%s,%s)'%(self.idx[0],self.idx[1],self.idx[2],self.v[0],self.v[1],self.v[2])

def vector( x,y,z=None ):
	if z:
		return Vector3( float(x),float(y),float(z) )
	else:
		return Vector3( float(x),float(y), 0.0 )

class adaptVec(list):
	def __init__(s,v):
		s.append(v.x)
		s.append(v.y)
		s.append(v.z)

