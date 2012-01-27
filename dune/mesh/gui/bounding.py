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

from dune.mesh.util.euclid import Vector3
from OpenGL.GL import *
from OpenGL.GLU import *
from dune.mesh.util.gridhelper import adaptVec
import math

class BoundingVolume:
	def __init__(s,mesh):
		s.outline_color = ( 1,1,1 )
		vertices = mesh.vertex_list.getVertices()
		minV = Vector3()
		maxV = Vector3()
		vertices.sort( lambda x, y: cmp(y.x, x.x ) )
		minV.x = vertices[0].x
		maxV.x = vertices[-1].x
		vertices.sort( lambda x, y: cmp(y.y, x.y ) )
		minV.y = vertices[0].y
		maxV.y = vertices[-1].y
		vertices.sort( lambda x, y: cmp(y.z, x.z ) )
		minV.z = vertices[0].z
		maxV.z = vertices[-1].z

		s.points = []
		for i in range(8):
			s.points.append(Vector3())
		for i in range(2):
			for j in range(2):
				s.points[int('%d%d%d'%(0,i,j),2)].x = minV.x
				s.points[int('%d%d%d'%(1,i,j),2)].x = maxV.x
				s.points[int('%d%d%d'%(i,0,j),2)].y = minV.y
				s.points[int('%d%d%d'%(i,1,j),2)].y = maxV.y
				s.points[int('%d%d%d'%(i,j,0),2)].z = minV.z
				s.points[int('%d%d%d'%(i,j,1),2)].z = maxV.z

		s.center = Vector3()
		for p in s.points:
			s.center += p
		s.center /= float(8)
		s.dl = glGenLists(1)
		glNewList(s.dl,GL_COMPILE)
		glLineWidth(5)
		c = s.outline_color
		glColor4f(c[0],c[1],c[2],0.2)
		glBegin(GL_LINE_STRIP)
		for v in s.points:
			glVertex(v())
		glEnd()
		c = s.points
		glBegin(GL_LINES)

		glVertex(c[0]())
		glVertex(c[2]())
		glVertex(c[6]())
		glVertex(c[4]())

		glVertex(c[1]())
		glVertex(c[3]())
		glVertex(c[7]())
		glVertex(c[5]())

		glVertex(c[0]())
		glVertex(c[1]())
		glVertex(c[3]())
		glVertex(c[2]())

		glVertex(c[2]())
		glVertex(c[3]())
		glVertex(c[7]())
		glVertex(c[6]())

		glVertex(c[7]())
		glVertex(c[6]())
		glVertex(c[4]())
		glVertex(c[5]())

		glVertex(c[0]())
		glVertex(c[1]())
		glVertex(c[5]())
		glVertex(c[4]())

		glEnd()
		glPushMatrix(  )
		glTranslatef(s.center.x,s.center.y,s.center.z)
		q = gluNewQuadric()
		gluSphere( q, GLdouble(0.25), GLint(10), GLint(10) )
		glPopMatrix(  )
		glEndList()

	def draw(s):
		glCallList(s.dl)

	def __repr__(s):
		ret = 'bounding box\n'
		for p in s.points:
			ret += '%s\n'%str(p)
		ret += '---\n'
		return ret

	def minViewDistance(s,viewangle=45.0):
		r = abs(s.center - s.points[0] )
		t = math.radians( (180 - viewangle)/ 2.0 )
		return 1.12 * r * math.tan(t)
