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

class Simplex3:
	def __init__(self,a,b,c,pl,f_id,color=None):
		assert isinstance(pl,MeshVertexList)
		assert isinstance(a,int)
		assert isinstance(b,int)
		assert isinstance(c,int)
		assert a!=b and b !=c and b!=c, 'degenerated simplex'
		assert a > -1, 'negative vertex id: %d / %d / %d'%(a,b,c)
		assert b > -1, 'negative vertex id: %d / %d / %d'%(a,b,c)
		assert c > -1, 'negative vertex id: %d / %d / %d'%(a,b,c)
		self.attribs = ( pl.attribs[a], pl.attribs[b], pl.attribs[c] )
		self.idx = ( a,b,c )
		ok = []
		#if oa != a or ob != b or oc != c:
			#for id in ( (a,oa) ,(b,ob),(c,oc)):
				#assert pl.verts[id[0]] == pl.verts[id[1]] , '%s%s%s -- %s\n%s'%(pl.verts[id[0]], ' -- ', pl.verts[id[1]], id, ok)
				#ok.append( id )
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
			try:
				self.v.append( pl[id] )
				self.center += pl[id]
			except IndexError, e:
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
	def __init__(self, dim):
		self.dim = dim
		self.vertices = []
		self.attribs = dict()
		#set to -1 so we get a 0-based index for verts dict
		self.duplicate_count = -1
		#alias -> real vertex id mapping
		self.aliases = dict()
		self.duplicates = []

	def addVertex(self,v,c):
		assert isinstance( c, Vector3 )
		assert isinstance( v, Vector3 )
		next_vertex_id = len(self.vertices) + len(self.duplicates)

		if not v in self.vertices:
			self.vertices.append(v)
			self.aliases[next_vertex_id] = next_vertex_id
		else:
			self.duplicates.append(v)
			self.aliases[next_vertex_id] = self.vertices.index( v )
		self.attribs[next_vertex_id] = c
		return next_vertex_id

	def __getitem__(self,idx):
		idx = self.aliases[idx]
		return self.vertices[idx]

	def __setitem__(self,idx,v):
		assert isinstance(idx,int)
		assert idx > -1
		assert isinstance(v, Vector3)
		idx = self.aliases[idx]
		self.vertices[idx] = v

	def realIndex(self,idx):
		if '__getitem__' in dir(idx):
			return map( lambda i: self.aliases[i], idx)
		else:
			return self.aliases[idx]

	def __len__(self):
		return len(self.vertices)