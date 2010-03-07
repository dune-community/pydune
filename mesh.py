#!/usr/bin/env python
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
from gridhelper import *
from euclid import *
from OpenGL.GL import *

def skipComments(fn):
	while fn:
		line = fn.readline()
		if line.startswith( '#' ):
			continue
		else:
			break
	return fn

def isAdjacentFace(fs,fa):
	for e in fs.edge_idx:
		e_ = ( e[1], e[0] )
		if e in fa.edge_idx or e_ in fa.edge_idx:
			return True
	return False

class Mesh():

	def __init__(self,dim):
		self.dim = dim
		self.vertices = PLCPointList(dim)
		self.faces = []
		self.edges = []
		self.draw_outline = True
		self.draw_faces = True
		self.outline_color = ( 1,1,1 )
		self.adj_points = dict()

	def parseSMESH(self, filename):
		self.parseSMESH_vertices(filename + '.vertices')
		self.parseSMESH_faces(filename + '.faces')
		self.buildAdjacencyList()
		#for k in self.adj[4]:
			#print self.faces[k].edge_idx
		#print '--\n',self.faces[4].edge_idx
		#print '---'


	def parseSMESH_vertices(self,filename):
		fn = open( filename, 'r' )
		for line in fn.readlines():
			if line.startswith( '#' ):
				continue
			line = line.split()
			#this way I can use vector for either dim
			line.append(None)
			v = vector( line[1], line[2], line[3] )
			self.vertices.appendVert( v )
		print len(self.vertices)
		fn.close()

	def parseSMESH_faces(self,filename):
		fn = open( filename, 'r' )
		for line in fn.readlines():
			if line.startswith( '#' ):
				continue
			line = line.split()
			#this way I can use vector for either dim
			line.append(None)
			v0 = int(line[1])
			v1 = int(line[2])
			v2 = int(line[3])
			s = simplex(self.vertices, v0,v1,v2 )
			if self.adj_points.has_key(v0) :
				self.adj_points[v0] += [ v1, v2 ] 
			else:
				self.adj_points[v0] = [ v1, v2 ]
			self.faces.append( s )
		print len(self.faces)
		fn.close()

	def buildAdjacencyList(self):
		self.adj = dict()
		i_s = 0
		for fs in self.faces:
			self.adj[i_s] = []
			ia = 0
			for fa in self.faces:
				if isAdjacentFace(fs,fa) and not ia == i_s:
					self.adj[i_s].append(ia)
				ia += 1
			i_s += 1
			
	def drawFace(self, f,opacity=1.):
		glBegin(GL_POLYGON)					# Start Drawing The Pyramid
		n = f.n
				#if i % 2 == 0:
					#n = -1.0 * n
		glNormal3f(n.x,n.y,n.z)
		for v in f.v:
			glColor4f(1.0,0,0,opacity)
			glVertex3f(v.x, v.y, v.z )
		glEnd()

	def drawOutline(self,f,opacity=1):
		glLineWidth(5)
		glBegin(GL_LINE_STRIP)
		n = f.n
		glNormal3f(n.x,n.y,n.z)
		for v in f.v:
			c = self.outline_color
			glColor4f(c[0],c[1],c[2],opacity)
			glVertex3f(v.x, v.y, v.z )
		glEnd()
				
	def drawAdjacentFaces( self, face_idx ):
		for f_idx in self.adj[face_idx]:
			self.drawOutline( self.faces[f_idx] )
			#self.drawFace( self.faces[f_idx], 0.5 )
		self.drawFace( self.faces[f_idx], 1.0 )
		self.drawOutline( self.faces[f_idx] )

	def draw(self, opacity=1.):
		if self.draw_faces:
			for f in self.faces:
				self.drawFace( f,opacity )
				
		if self.draw_outline:
			for f in self.faces:
				self.drawOutline(f)

	def smooth(self,weight=1.0):
		print '%d -- %d'%(len(self.adj_points) ,len(self.vertices.verts))
		for i,v in self.vertices.verts.iteritems():
			if self.adj_points.has_key(i):
				n = len( self.adj_points[i] )
				if n > 0:
					s = Vector3()
					for j in self.adj_points[i]:
						s += weight * self.vertices.verts[j]
					s /= float(n)
					self.vertices.verts[i] = s
		for f in self.faces:
			f.reset(self.vertices)
		print self.adj_points.keys()
		print self.vertices.verts[1]
		print self.vertices.verts[26]