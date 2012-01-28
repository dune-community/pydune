#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
mesh.py (c) 2009 rene.milk@uni-muenster.de
Licence: WTFPLv2, see LICENSE.txt
"""

from OpenGL.GL import (glBegin, glVertex3fv, glPushMatrix, glTranslatef,
	glPopMatrix, glEndList, glCallList, glColor4f, glNewList, GL_COMPILE,
	GL_LINE_STRIP, GL_LINES, glVertex, glEnd, glGenLists, glLineWidth,
	GLdouble, GLint, glEnd)
from OpenGL.GLU import (gluNewQuadric, gluSphere)
from dune.mesh.util.euclid import Vector3
from dune.mesh.util.gridhelper import adaptVec
import math

class BoundingVolume:
	def __init__(self,mesh):
		self.outline_color = (1, 1, 1)
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

		self.points = []
		for i in range(8):
			self.points.append(Vector3())
		for i in range(2):
			for j in range(2):
				self.points[int('%d%d%d'%(0,i,j),2)].x = minV.x
				self.points[int('%d%d%d'%(1,i,j),2)].x = maxV.x
				self.points[int('%d%d%d'%(i,0,j),2)].y = minV.y
				self.points[int('%d%d%d'%(i,1,j),2)].y = maxV.y
				self.points[int('%d%d%d'%(i,j,0),2)].z = minV.z
				self.points[int('%d%d%d'%(i,j,1),2)].z = maxV.z

		self.center = Vector3()
		for p in self.points:
			self.center += p
		self.center /= float(8)
		self.dl = glGenLists(1)
		glNewList(self.dl,GL_COMPILE)
		glLineWidth(5)
		c = self.outline_color
		glColor4f(c[0],c[1],c[2],0.2)
		glBegin(GL_LINE_STRIP)
		for v in self.points:
			glVertex(v())
		glEnd()
		c = self.points
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
		glTranslatef(self.center.x,self.center.y,self.center.z)
		q = gluNewQuadric()
		gluSphere( q, GLdouble(0.25), GLint(10), GLint(10) )
		glPopMatrix(  )
		glEndList()

	def draw(self):
		glCallList(self.dl)

	def __repr__(self):
		ret = 'bounding box\n'
		for p in self.points:
			ret += '%s\n'%str(p)
		ret += '---\n'
		return ret

	def minViewDistance(self, viewangle=45.0):
		r = abs(self.center - self.points[0] )
		t = math.radians( (180 - viewangle)/ 2.0 )
		return 1.12 * r * math.tan(t)
