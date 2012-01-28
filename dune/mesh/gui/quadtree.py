#!/usr/bin/env python
"""
mesh.py (c) 2009 rene.milk@uni-muenster.de
Licence: WTFPLv2, see LICENSE.txt
"""


from OpenGL.GL import (glBegin, glVertex3fv, glPushMatrix, glTranslatef,
	glPopMatrix, glEndList, glCallList, glColor4f, glNewList, glEnd,
	GLdouble, glGenLists, GL_COMPILE, GLint, GL_QUADS )
from OpenGL.GLU import (gluNewQuadric, gluSphere)
from dune.mesh.util.gridhelper import adaptVec


class Box:
	def __init__(self,points):
		assert len(points)==8
		self.corners = points[:]
		self.dl = glGenLists(1)
		self.prepDraw()
		
	def prepDraw(self):
		glNewList(self.dl,GL_COMPILE)
		
		c = self.corners
		for h in c:
			glPushMatrix(  )
			glTranslatef(h.x,h.y,h.z)
			q = gluNewQuadric()
			gluSphere( q, GLdouble(0.45), GLint(10), GLint(10) )
			glPopMatrix(  )

		glBegin(GL_QUADS)

		glVertex3fv(adaptVec(c[0]))
		glVertex3fv(adaptVec(c[2]))
		glVertex3fv(adaptVec(c[6]))
		glVertex3fv(adaptVec(c[4]))

		glVertex3fv(adaptVec(c[1]))
		glVertex3fv(adaptVec(c[3]))
		glVertex3fv(adaptVec(c[7]))
		glVertex3fv(adaptVec(c[5]))

		glVertex3fv(adaptVec(c[0]))
		glVertex3fv(adaptVec(c[1]))
		glVertex3fv(adaptVec(c[3]))
		glVertex3fv(adaptVec(c[2]))

		glVertex3fv(adaptVec(c[2]))
		glVertex3fv(adaptVec(c[3]))
		glVertex3fv(adaptVec(c[7]))
		glVertex3fv(adaptVec(c[6]))

		glVertex3fv(adaptVec(c[7]))
		glVertex3fv(adaptVec(c[6]))
		glVertex3fv(adaptVec(c[4]))
		glVertex3fv(adaptVec(c[5]))

		glVertex3fv(adaptVec(c[0]))
		glVertex3fv(adaptVec(c[1]))
		glVertex3fv(adaptVec(c[5]))
		glVertex3fv(adaptVec(c[4]))

		glEnd()
		glEndList()
		
	def draw(self):
		glCallList(self.dl)

	def scale(self,f):
		for h in self.corners:
			h *= f
		self.prepDraw()

	def translate(self,v):
		for h in self.corners:
			h += v
		self.prepDraw()

class Quadtree:
	def __init__(self,mesh):
		self.box = mesh.bounding_box.points
		self.children = []
		p = mesh.bounding_box.points[:]
		b = Box( p )
		v = p[7]
		b.translate( -v )
		b.scale(0.5)
		b.translate( v )
		
		self.children.append( b )
		c = Box(b.corners)
		c.translate( (p[6] - p[7]) )
		self.children.append( c )
		d = Box(c.corners)
		d.translate( p[5] - p[7] - p[1] )
		self.children.append( d )
		e = Box(d.corners)
		e.translate( - p[7] - p[1] )
		self.children.append( e )
		f = Box(e.corners)
		f.translate( - p[5] +p[4] )
		self.children.append( f )
		g = Box(e.corners)
		g.translate( +p[4] - p[0] )
		self.children.append( g )
		h = Box(e.corners)
		h.translate( +p[3] - p[2] )
		self.children.append( h )
		i = Box(e.corners)
		i.translate( - p[7] + p[4] )
		self.children.append( i )

	def draw(self):
		n = float( len(self.children) )
		i = 0
		for b in self.children:
			glColor4f(1-i/n,i/n,0,0.5)
			b.draw()
			i += 1
