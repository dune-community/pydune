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
from PyQt4 import QtCore, QtGui, QtOpenGL

class ControlPanel(QtGui.QWidget):
	def __init__(self, parent):
		super(ControlPanel, self).__init__(parent)
		box = QtGui.QVBoxLayout();

		assert parent
		self.viewer = parent

		self.setWindowTitle("Control Panel")
		self.resize(200, 320)
		groupBox = QtGui.QGroupBox("Smoothing parameters");
		grid = QtGui.QGridLayout()
		groupBox.setLayout( grid )
		box.addWidget( groupBox )
		lambdaLabel = QtGui.QLabel("Step Size (lambda)")
		grid.addWidget( lambdaLabel, 0,0 )
		self.lambdaSpinBox = QtGui.QDoubleSpinBox()
		self.lambdaSpinBox.setRange(0.0, 20.0)
		self.lambdaSpinBox.setSingleStep(0.01)
		self.lambdaSpinBox.setValue(0.01)
		grid.addWidget( self.lambdaSpinBox, 0,1 )
		iterationsLabel = QtGui.QLabel("# iterations")
		grid.addWidget( iterationsLabel, 1,0 )
		self.iterationsSpinBox = QtGui.QSpinBox()
		self.iterationsSpinBox.setRange(1, 120.0)
		self.iterationsSpinBox.setSingleStep(1)
		self.iterationsSpinBox.setValue(1)
		grid.addWidget( self.iterationsSpinBox, 1,1 )
		
		grid2 = QtGui.QGridLayout()
		groupBox2 = QtGui.QGroupBox("Smoothing algorithm");
		laplaceButton = QtGui.QPushButton("L&aplace")
		laplaceButton.setFocusPolicy(QtCore.Qt.NoFocus)
		laplaceButton.clicked.connect(self.viewer.smoothLaplace)
		grid2.addWidget( laplaceButton, 0,0 )
		normalButton = QtGui.QPushButton("Mean &Normal")
		normalButton.setFocusPolicy(QtCore.Qt.NoFocus)
		normalButton.clicked.connect(self.viewer.smoothMeanNormal)
		grid2.addWidget( normalButton, 1,0 )
		random_noiseButton = QtGui.QPushButton("Random No&ise")
		random_noiseButton.setFocusPolicy(QtCore.Qt.NoFocus)
		random_noiseButton.clicked.connect(self.viewer.noise)
		grid2.addWidget( random_noiseButton, 2,0 )
		
		groupBox2.setLayout( grid2 )
		box.addWidget( groupBox2 )

		grid3 = QtGui.QGridLayout()
		groupBox3 = QtGui.QGroupBox("View");
		resetButton = QtGui.QPushButton("&Reset")
		resetButton.setFocusPolicy(QtCore.Qt.NoFocus)
		resetButton.clicked.connect(self.viewer.reset)
		grid3.addWidget( resetButton, 0,0 )
		self.draw_bounding_box = QtGui.QCheckBox("Show &bounding box", self)
		self.draw_bounding_box.stateChanged.connect(self.viewer.setOptions)
		grid3.addWidget( self.draw_bounding_box, 1,0 )
		self.draw_mesh = QtGui.QCheckBox("Show &mesh", self)
		self.draw_mesh.stateChanged.connect(self.viewer.setOptions)
		grid3.addWidget( self.draw_mesh, 2,0 )
		#self.point_num = QtGui.QSpinBox()
		#self.point_num.setRange(0, 8000.0)
		#self.point_num.setSingleStep(1)
		#self.point_num.setValue(1)
		#self.point_num.valueChanged.connect(self.viewer.setPointDraw)
		#grid3.addWidget( self.point_num, 2,0 )
		subbox1 = QtGui.QGroupBox("Restrict");
		subgrid1 = QtGui.QGridLayout()
		self.enable_restrict = QtGui.QCheckBox("Enable", self)
		self.enable_restrict.stateChanged.connect(self.viewer.enable_restrict)
		subgrid1.addWidget(  self.enable_restrict, 0, 0 )
		self.slider_min = QtGui.QSlider(QtCore.Qt.Horizontal)
		self.slider_max = QtGui.QSlider(QtCore.Qt.Horizontal)
		self.setMinMaxSlider()
		subgrid1.addWidget(  self.slider_min, 1, 0 )
		subgrid1.addWidget(  self.slider_max, 2, 0 )
		subbox1.setLayout( subgrid1 )
		grid3.addWidget( subbox1, 3,0 )
		
		groupBox3.setLayout( grid3 )
		box.addWidget( groupBox3 )
		
		grid4 = QtGui.QGridLayout()
		groupBox4 = QtGui.QGroupBox("Save/Load");
		loadButton = QtGui.QPushButton("&Load")
		loadButton.setFocusPolicy(QtCore.Qt.NoFocus)
		loadButton.clicked.connect(self.viewer.load)
		grid4.addWidget( loadButton, 0,0 )
		saveButton = QtGui.QPushButton("Sa&ve")
		saveButton.setFocusPolicy(QtCore.Qt.NoFocus)
		saveButton.clicked.connect(self.viewer.save)
		grid4.addWidget( saveButton, 1,0 )
		reloadButton = QtGui.QPushButton("R&eload")
		reloadButton.setFocusPolicy(QtCore.Qt.NoFocus)
		reloadButton.clicked.connect(self.viewer.reload)
		grid4.addWidget( reloadButton, 2,0 )
		groupBox4.setLayout( grid4 )
		box.addWidget( groupBox4 )
		
		self.setLayout(box)

		#connect only now lest be called on manual set
		self.slider_max.valueChanged.connect(self.viewer.set_restrict)
		self.slider_min.valueChanged.connect(self.viewer.set_restrict)

	def setMinMaxSlider(s):
		mx = len(s.viewer.widget.mesh.faces)
		for sl in [ s.slider_min , s.slider_max ]:
			sl.setMinimum( 0 )
			sl.setMaximum( mx )
			sl.setFocusPolicy(QtCore.Qt.StrongFocus)
			sl.setTickInterval(mx/10)
			sl.setSingleStep(1)
		s.slider_min.setValue(0)
		s.slider_min.setTickPosition(QtGui.QSlider.TicksAbove)
		s.slider_max.setTickPosition(QtGui.QSlider.TicksBelow)
		s.slider_max.setValue(mx)


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
		white_light = ( 1., 1., 1., 0.501 )
		d_light = ( 1., 1., 1., 0.01 )
		spec = ( 1., 1., 1., 0.08 )
		glLightfv(GL_LIGHT0, GL_POSITION, light_position )
		glLightfv(GL_LIGHT0, GL_AMBIENT,  white_light )
		#glLightfv(GL_LIGHT0, GL_DIFFUSE,  d_light )
		glLightfv(GL_LIGHT0, GL_SPECULAR, spec )

		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)

		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
		#glBlendFunc(GL_SRC_ALPHA,GL_ONE)
		glColorMaterial ( GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE  )
		glEnable(GL_COLOR_MATERIAL)
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

	def paintGL(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)	# Clear The Screen And The Depth Buffer
		h = self.size().height()
		w = self.size().width()
		glEnable(GL_DEPTH_TEST)
		glViewport(0, 0, w, h)		# Reset The Current Viewport And Perspective Transformation
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(45.0, float(w)/float(h), 0.1, 1000000.0)
		glMatrixMode(GL_MODELVIEW)
		
		glLoadIdentity()					# Reset The View
		glEnable(MeshWidget.GL_MULTISAMPLE)
		glTranslatef(0,0.0,self.zoom)
		glRotate(self.rotation[0], 0.0, 1.0, 0.0)
		glRotate(self.rotation[1], 1.0, 0.0, 0.0)

		center = -self.mesh.bounding_box.center
		glTranslatef(center.x,center.y,center.z)

		if self.draw_mesh:
			if self.enable_restrict:
				for i in self.restricted:
					glBegin(GL_TRIANGLES)
					self.mesh.drawFaceIdx(i)
					glEnd()
			else:
				self.mesh.draw(1.0)
		if self.draw_bounding_box:
			self.mesh.bounding_box.draw()
		if self.draw_octree:
			self.mesh.quad.draw()

		#single vertex marker
		#glPushMatrix(  )
		#s = self.mesh.vertices.verts[self.point_draw]
		#glTranslatef(s.x,s.y,s.z)
		#q = gluNewQuadric()
		#gluSphere( q, GLdouble(0.65), GLint(10), GLint(10) )
		#glPopMatrix(  )
		
		#self.mesh.drawAdjacentFaces( self.count )
		#self.count += 1
		#if self.count == len(self.mesh.faces):
			#self.count = 0
		#time.sleep(0.3)
		#self.mesh.smooth(0.45)
		w /= 5
		h /= 5
		glViewport(0, 0, w, h)		# Reset The Current Viewport And Perspective Transformation
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(45.0, float(w)/float(h), 0.1, 1000000.0)
		glMatrixMode(GL_MODELVIEW)
		glDisable(GL_DEPTH_TEST)
		glLoadIdentity()					# Reset The View
		glTranslatef(0,0.0,-self.mesh.bounding_box.minViewDistance())
		glRotate(self.rotation[0], 0.0, 1.0, 0.0)
		glRotate(self.rotation[1], 1.0, 0.0, 0.0)

		center = -self.mesh.bounding_box.center
		glTranslatef(center.x,center.y,center.z)

		if self.draw_mesh:
			self.mesh.draw(0.5)


	def wheelEvent( self, event):
		self.zoom += ( event.delta() / 120 ) * 5
		self.update()

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
		
	def __init__(self, parent,filename):
		super(QtOpenGL.QGLWidget, self).__init__(QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers), parent)
		#super(GLWidget, self).__init__(QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers), parent)
		self.setMinimumSize(1024, 768)
		self.count = 0
		self.draw_bounding_box = self.draw_octree = False
		self.draw_mesh = True

		self.mesh = mesh.Mesh( 3 )
		self.mesh.parse( filename )
		self.setAutoBufferSwap(True)
		self.initializeGL()
		self.zoom = -self.mesh.bounding_box.minViewDistance()
		self.enable_restrict = False
		self.restricted = range(len(self.mesh.faces))
		self.point_draw = 1

	def reset(s):
		s.rotation=[0,0]
		s.prev_mouse = (0,0)
		s.zoom = -s.mesh.bounding_box.minViewDistance()
		s.update()
	

class MeshViewer(QtGui.QMainWindow):
	ESCAPE = '\033'
	
	def __init__(self,filename=None):
		QtGui.QMainWindow.__init__(self)
		if filename:
			self.filename = filename
		else:
			self.filename = sys.argv[1]
		self.widget = MeshWidget(self,self.filename)
		self.setCentralWidget(self.widget)
		self.cp = ControlPanel(self)
		self.cp.draw_bounding_box.setChecked( self.widget.draw_bounding_box )
		self.cp.draw_mesh.setChecked( self.widget.draw_mesh )
		cpDock = QtGui.QDockWidget("Control Panel", self)
		cpDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
		cpDock.setWidget( self.cp )
		self.addDockWidget(0x2,cpDock )

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

	def smoothLaplace(self):
		for i in range(self.cp.iterationsSpinBox.value()):
			self.widget.mesh.smooth(self.cp.lambdaSpinBox.value())
			self.widget.update()

	def smoothMeanNormal(self):
		for i in range(self.cp.iterationsSpinBox.value()):
			self.widget.mesh.smooth2()
			self.widget.update()

	def reset(self):
		self.cp.setMinMaxSlider()
		self.widget.reset()
		self.widget.update()

	def setOptions(s):
		s.widget.draw_bounding_box = s.cp.draw_bounding_box.isChecked()
		s.widget.draw_mesh = s.cp.draw_mesh.isChecked()
		s.widget.update()

	def noise(s):
		for i in range(s.cp.iterationsSpinBox.value()):
			s.widget.mesh.noise( s.cp.lambdaSpinBox.value() )
			s.widget.update()

	def reload(s):
		s.widget.mesh.parse( s.filename )
		s.widget.mesh.prepDraw()
		s.widget.update()

	def save(s):
		s.filename = str(QtGui.QFileDialog.getSaveFileName(s,'Select file to save to'))
		s.filename = s.widget.mesh.write( s.filename )
		s.widget.update()

	def load(s):
		s.filename = str(QtGui.QFileDialog.getOpenFileName(s,'Select file to load'))
		s.reload()

	def enable_restrict(s):
		pass

	def set_restrict(s,k):
		s.widget.enable_restrict = s.cp.enable_restrict.isChecked()
		s.widget.restricted = range( s.cp.slider_min.value(), s.cp.slider_max.value() )
		s.widget.update()
		print  s.cp.slider_min.value(), s.cp.slider_max.value()

	def setPointDraw(s):
		s.widget.point_draw = s.cp.point_num.value()
		s.widget.update()
		
if __name__ == '__main__':
	app = QtGui.QApplication(['MeshViewer'])
	window = MeshViewer()
	window.show()
	app.exec_()

