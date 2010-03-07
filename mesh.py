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

class Mesh():

	def __init__(self,dim):
		self.dim = dim
		self.vertices = PLCPointList(dim)
		self.faces = []

	def parseSMESH(self, filename):
		self.parseSMESH_vertices(filename + '.vertices')
		self.parseSMESH_faces(filename + '.faces')

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

	def parseSMESH_faces(self,filename):
		fn = open( filename, 'r' )
		for line in fn.readlines():
			if line.startswith( '#' ):
				continue
			line = line.split()
			#this way I can use vector for either dim
			line.append(None)
			s = simplex(self.vertices, int(line[1]),int(line[2]),int(line[3]) )
			self.faces.append( s )
		print len(self.faces)
			
	def draw(self):
		glBegin(GL_TRIANGLES)					# Start Drawing The Pyramid
		i = 0
		for f in self.faces:
			n = f.n
			if i % 2 == 0:
				n = -1.0 * n
			glNormal3f(n.x,n.y,n.z)
			for v in f.v:
				glColor3f(1.0,0,0)
				glVertex3f(v.x, v.y, v.z )
		glEnd()