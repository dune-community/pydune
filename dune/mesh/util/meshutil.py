#!/usr/env/python
# -*- coding: utf-8 -*-
"""
gridhelper.py (c) 2009 rene.milk@uni-muenster.de
Licence: WTFPLv2, see LICENSE.txt
"""

import math
import copy
from euclid import *
import colors

class DimensionIncompatibleException(Exception):
	pass

class ImpossibleException(Exception):
	pass

class ColorToBoundaryIdMapper:
	def __init__(self):
		self.known_colors = []
		self.eps = 5e-1

	def getID(self, color):
		assert isinstance( color, Vector3 )
		idx = -1
		for c in self.known_colors:
			if abs(c - color) < self.eps:
				idx = self.known_colors.index(c)
				return idx + 1
		self.known_colors.append(color)
		return self.known_colors.index(color) + 1

	def __repr__(self):
		return '%d Colors: '%(len(self.known_colors)) + ' '.join( map(lambda p: str(p), self.known_colors ) )

class BoundaryIdToColorMapper:
	def __init__(self,expected=11):
		self.bids = []
		self.expected = expected
		self.colormap = colors.getColourPaletteCheat(expected,[(0.0,0,0.0)])

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

class Simplex3:
	def __init__(self,a,b,c,pl,f_id,color=None,boundary_id=None):
		assert isinstance(pl,MeshVertexList)
		assert isinstance(a,int)
		assert isinstance(b,int)
		assert isinstance(c,int)
		assert a!=b and b !=c and b!=c, 'degenerated simplex'
		max_id = len(pl)
		assert a > -1 and a <= max_id, 'negative vertex id: %d / %d / %d'%(a,b,c)
		assert b > -1 and b <= max_id, 'negative vertex id: %d / %d / %d'%(a,b,c)
		assert c > -1 and c <= max_id, 'negative vertex id: %d / %d / %d'%(a,b,c)
		self.attribs = ( pl.attribs[a], pl.attribs[b], pl.attribs[c] )
		self.idx = ( a,b,c )
		self.edge_idx = ( (a,b), (b,c), (c,a) )
		self.id = f_id
		self.reset(pl)
		self.m = Vector3()
		if color != None:
			self.color = color
		else:
			self.color = self.attribs[0]/255.0
		self.boundary_id = boundary_id

	def reset(self,pl):
		self.v = []
		self.center = Vector3()
		
		for id in self.idx:
			try:
				self.v.append( pl[id] )
				self.center += pl[id]
			except IndexError, e:
				import traceback
				print traceback.format_exc()
				print self.idx, id
				raise e
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

class MeshVertexList(object):
	def __init__(self, dim=3):
		self.__vertices = dict()
		self.attribs = dict()
		#alias -> real vertex id mapping
		self.aliases = dict()
		self.duplicates = []

	def addVertex(self,v,c):
		assert isinstance( c, Vector3 )
		assert isinstance( v, Vector3 )
		next_vertex_id = len(self.__vertices) + len(self.duplicates)

		if not v in self.__vertices:
			self.__vertices[next_vertex_id] = v
			self.aliases[next_vertex_id] = next_vertex_id
		else:
			self.duplicates.append(v)
			self.aliases[next_vertex_id] = self.__vertices.index( v )
		self.attribs[next_vertex_id] = c
		return next_vertex_id

	def __getitem__(self,idx):
		assert idx in self.aliases.keys()
		real_idx = self.aliases[idx]
		#assert len(self.__vertices) >  real_idx , 'v %d -- r %d| len %d'%(idx, real_idx,len(self.__vertices))
		return self.__vertices[real_idx]

	def __setitem__(self,idx,v):
		assert isinstance(idx,int)
		assert idx > -1
		assert isinstance(v, Vector3)
		idx = self.aliases[idx]
		self.__vertices[idx] = v

	def realIndex(self,idx):
		if '__getitem__' in dir(idx):
			return map( lambda i: self.aliases[i], idx)
		else:
			return self.aliases[idx]

	def __len__(self):
		return len(self.__vertices)

	def getVertices(s):
		return s.__vertices.values()[:]

def find_key(dic, val):
	"""return the key of dictionary dic given the value"""
	return [k for k, v in dic.iteritems() if v == val][0]
