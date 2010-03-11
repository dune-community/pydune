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

import mesh,sys,time,math
from OpenGL.GL import *
#from OpenGL.GLUT import *
from OpenGL.GLU import *
from PyQt4 import QtGui
from PyQt4 import QtCore, QtGui, QtOpenGL


# A general OpenGL initialization function.  Sets all of the initial parameters.
class MeshWidget(QtOpenGL.QGLWidget):
	GL_MULTISAMPLE = 0x809D
	
	def initializeGL(self):				# We call this right after our OpenGL window is created.
		glClearColor(0.0, 0.0, 0.0, 1.0)	# This Will Clear The Background Color To Black
		glClearDepth(1.0)					# Enables Clearing Of The Depth Buffer
		glDepthFunc(GL_LESS)				# The Type Of Depth Test To Do
		glEnable(GL_DEPTH_TEST)				# Enables Depth Testing
		glShadeModel(GL_SMOOTH)				# Enables Smooth Color Shading

		glEnable(GL_NORMALIZE)
		light_position = ( 0., 0., 1., 0. )
		white_light = ( 1., 1., 1., 0.01 )
		d_light = ( 1., 1., 1., 0.1 )
		red_light = ( 1., 0., 0., 0.7 )
		glLightfv(GL_LIGHT0, GL_POSITION, light_position)
		glLightfv(GL_LIGHT1, GL_POSITION, light_position)
		glLightfv(GL_LIGHT0, GL_AMBIENT, white_light)
		#glLightfv(GL_LIGHT1, GL_AMBIENT, ( 1., 1., 1., 0.8 ) )
		glLightfv(GL_LIGHT1, GL_SPECULAR, red_light)
		glLightfv(GL_LIGHT0, GL_DIFFUSE, d_light)

		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)
		#glEnable(GL_LIGHT1)

		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
		#glBlendFunc(GL_SRC_ALPHA,GL_ONE)
		glColorMaterial ( GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE  )
		#glEnable(GL_COLOR_MATERIAL)
		glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()					# Reset The Projection Matrix

		gluPerspective(45.0, float(self.size().height())/float(self.size().width()), 0.1, 1000000.0)

		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		self.rotation = [0.0, 0.0]
		self.mesh.prepDraw()
		#glEnable(GL_CULL_FACE)

	# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
	def resizeGL(self, w, h):
		if h == 0:						# Prevent A Divide By Zero If The Window Is Too Small
			h = 1

		glViewport(0, 0, w, h)		# Reset The Current Viewport And Perspective Transformation
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(45.0, float(w)/float(h), 0.1, 1000000.0)
		glMatrixMode(GL_MODELVIEW)

	def paintGL(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)	# Clear The Screen And The Depth Buffer
		glLoadIdentity()					# Reset The View
		glEnable(MeshWidget.GL_MULTISAMPLE)
		glTranslatef(0,0.0,self.zoom)
		glRotate(self.rotation[0], 0.0, 1.0, 0.0)
		glRotate(self.rotation[1], 1.0, 0.0, 0.0)

		center = -self.mesh.bounding_box.center
		glTranslatef(center.x,center.y,center.z)

		if self.draw_mesh:
			self.mesh.draw(1.0)
		#if self.draw_bounding_box:
			#self.mesh.bounding_box.draw()
		#if self.draw_octree:
			#self.mesh.quad.draw()
		#self.mesh.drawAdjacentFaces( self.count )
		#self.count += 1
		#if self.count == len(self.mesh.faces):
			#self.count = 0
		#time.sleep(0.3)
		#self.mesh.smooth(0.45)

	def processMouse( wheel, direction,x,y):
		self.zoom += direction * 5

	def mousePressEvent(self, event):
		self.prev_mouse = (event.x(), event.y())

	def mouseMoveEvent(self, event):
		x = event.x()
		y = event.y()

		sensitivity = 0.2
		mouse_x,mouse_y = self.prev_mouse
		self.rotation[0] -= sensitivity*(mouse_x-x);
		self.rotation[1] -= sensitivity*(mouse_y-y);
		self.prev_mouse = (x,y)
		self.update()
		event.accept()
		
	def __init__(self, parent):
		super(QtOpenGL.QGLWidget, self).__init__(QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers), parent)
		#super(GLWidget, self).__init__(QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers), parent)
		self.setMinimumSize(1024, 768)
		self.zoom = -20.
		self.count = 0
		self.draw_bounding_box = self.draw_octree = False
		self.draw_mesh = True
		filename = sys.argv[1]

		self.mesh = mesh.Mesh( 3 )
		dd = filename.find('phantom') != -1
		self.mesh.parseSMESH( filename, dd )
		self.setAutoBufferSwap(True)

class MeshViewer(QtGui.QMainWindow):
	ESCAPE = '\033'
	
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		self.widget = MeshWidget(self)
		self.setCentralWidget(self.widget)

	def keyPressEvent(self, event):
		args = [event.text()]
		# If escape is pressed, kill everything.
		if args[0] == MeshViewer.ESCAPE:
			sys.exit()
		if args[0] == '1':
			self.widget.mesh.smooth(0.1)
		if args[0] == '3':
			c = 40
			for i in range(c):
				self.widget.mesh.smooth(0.01)
			print '%d smooth1 iterations completed'%c
		if args[0] == '2':
			self.widget.mesh.smooth2(10)
		if args[0] == 'n':
			self.widget.mesh.noise(0.1)
		if args[0] == '+':
			self.widget.zoom += 5
		if args[0] == '-':
			self.widget.zoom -= 5
		if args[0] == 'b':
			self.widget.draw_bounding_box = not self.widget.draw_bounding_box
		if args[0] == 'o':
			self.widget.draw_octree = not self.widget.draw_octree
		if args[0] == 'm':
			self.widget.draw_mesh = not self.widget.draw_mesh
		if args[0] == 'c':
			glEnable(GL_COLOR_MATERIAL)
		self.widget.update()
		event.accept()
		
if __name__ == '__main__':
	app = QtGui.QApplication(['MeshViewer'])
	window = MeshViewer()
	window.show()
	app.exec_()

