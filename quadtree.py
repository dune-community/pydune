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
import random
from OpenGL.GL import *
from OpenGL.GLUT import *

class Box:
	def __init__(s,points):
		assert len(points)==8
		s.corners = points[:]
		s.dl = glGenLists(1)
		s.prepDraw()
		
	def prepDraw(s):
		glNewList(s.dl,GL_COMPILE)
		
		c = s.corners
		for h in c:
			glPushMatrix(  )
			glTranslatef(h.x,h.y,h.z)
			glutSolidSphere( GLdouble(0.45), GLint(10), GLint(10) )
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
		
	def draw(s):
		glCallList(s.dl)

	def scale(s,f):
		for h in s.corners:
			h *= f
		s.prepDraw()

	def translate(s,v):
		for h in s.corners:
			h += v
		s.prepDraw()

class Quadtree:
	def __init__(s,mesh):
		s.box = mesh.bounding_box.points
		s.children = []
		p = mesh.bounding_box.points[:]
		b = Box( p )
		v = p[7]
		b.translate( -v )
		b.scale(0.5)
		b.translate( v )
		
		s.children.append( b )
		c = Box(b.corners)
		c.translate( (p[6] - p[7]) )
		s.children.append( c )
		d = Box(c.corners)
		d.translate( p[5] - p[7] - p[1] )
		s.children.append( d )
		e = Box(d.corners)
		e.translate( - p[7] - p[1] )
		s.children.append( e )
		f = Box(e.corners)
		f.translate( - p[5] +p[4] )
		s.children.append( f )
		g = Box(e.corners)
		g.translate( +p[4] - p[0] )
		s.children.append( g )
		h = Box(e.corners)
		h.translate( +p[3] - p[2] )
		s.children.append( h )
		i = Box(e.corners)
		i.translate( - p[7] + p[4] )
		s.children.append( i )

	def draw(s):
		n = float( len(s.children) ) 
		i = 0
		for b in s.children:
			glColor4f(1-i/n,i/n,0,0.5)
			b.draw()
			i += 1