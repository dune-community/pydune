#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
widgets.py (c) 2009 rene.milk@uni-muenster.de
Licence: WTFPLv2, see LICENSE.txt
"""

import sys
import time
import math
import Image
from OpenGL.GL import (glBegin, glVertex3fv, glPushMatrix, glTranslatef,
	glPopMatrix, glEndList, glCallList, glColor4f, glNewList,
	glClear, glClearColor, glColorMaterial, glBlendFunc, glClearDepth,
	glDisable, glEnable, glHint, glLightfv, glLoadIdentity, glMatrixMode,
	glReadPixels, glRotate, glShadeModel, glViewport, glDepthFunc, glEnd,
	GL_AMBIENT, GL_AMBIENT_AND_DIFFUSE, GL_BLEND, GL_COLOR_BUFFER_BIT,
	GL_COLOR_MATERIAL, GL_CULL_FACE, GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST,
	GL_DIFFUSE, GL_FRONT_AND_BACK, GL_LESS, GL_LIGHT0, GL_LIGHTING,
	GL_MODELVIEW, GL_MULTISAMPLE, GL_NICEST, GL_NORMALIZE, GL_ONE,
	GL_ONE_MINUS_SRC_ALPHA, GL_PERSPECTIVE_CORRECTION_HINT, GL_POSITION,
	GL_PROJECTION, GL_RGBA, GL_SMOOTH, GL_SPECULAR, GL_SRC_ALPHA,
	GL_TRIANGLES, GL_UNSIGNED_BYTE)
from OpenGL.GLU import (gluNewQuadric, gluPerspective, gluSphere)
from PyQt4 import QtCore, QtGui, QtOpenGL
from dune.mesh import mesh 

class BidPanel(object):
	def __init__(self, parent, mesh):
		super(BidPanel, self).__init__()
		for bid, colors in mesh.bid_color_mapping.iteritems():
			print('BID %d: %s' % (bid,' '.join(set(
						[str((255*c.x,255*c.y,255*c.z)) for c in colors])) ))
		
class ControlPanel(QtGui.QWidget):
	def __init__(self, parent, bid_widget):
		super(ControlPanel, self).__init__(parent)
		box = QtGui.QVBoxLayout()

		assert parent
		self.viewer = parent

		self.setWindowTitle("Control Panel")
		self.resize(200, 320)
		groupBox = QtGui.QGroupBox("Smoothing parameters")
		grid = QtGui.QGridLayout()
		groupBox.setLayout( grid )
		box.addWidget( groupBox )
		lambdaLabel = QtGui.QLabel("Step Size (lambda)")
		grid.addWidget( lambdaLabel, 0, 0 )
		self.lambdaSpinBox = QtGui.QDoubleSpinBox()
		self.lambdaSpinBox.setRange(0.0, 20.0)
		self.lambdaSpinBox.setSingleStep(0.01)
		self.lambdaSpinBox.setValue(0.01)
		grid.addWidget( self.lambdaSpinBox, 0, 1 )
		iterationsLabel = QtGui.QLabel("# iterations")
		grid.addWidget( iterationsLabel, 1, 0 )
		self.iterationsSpinBox = QtGui.QSpinBox()
		self.iterationsSpinBox.setRange(1, 120.0)
		self.iterationsSpinBox.setSingleStep(1)
		self.iterationsSpinBox.setValue(1)
		grid.addWidget( self.iterationsSpinBox, 1, 1 )

		grid2 = QtGui.QGridLayout()
		groupBox2 = QtGui.QGroupBox("Smoothing algorithm")
		laplaceButton = QtGui.QPushButton("L&aplace")
		laplaceButton.setFocusPolicy(QtCore.Qt.NoFocus)
		laplaceButton.clicked.connect(self.viewer.smoothLaplace)
		grid2.addWidget( laplaceButton, 0, 0 )
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
		groupBox3 = QtGui.QGroupBox("View")
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
		subbox1 = QtGui.QGroupBox("Restrict")
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
		groupBox4 = QtGui.QGroupBox("Save/Load")
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
		screenieButton = QtGui.QPushButton("Screenshot")
		screenieButton.setFocusPolicy(QtCore.Qt.NoFocus)
		screenieButton.clicked.connect(self.viewer.saveScreenshot)
		grid4.addWidget( screenieButton, 3,0 )
		groupBox4.setLayout( grid4 )
		box.addWidget( groupBox4 )

		#box.addWidget(bid_widget)
		self.setLayout(box)

		#connect only now lest be called on manual set
		self.slider_max.valueChanged.connect(self.viewer.set_restrict)
		self.slider_min.valueChanged.connect(self.viewer.set_restrict)

	def setMinMaxSlider(self):
		mx = len(self.viewer.widget.mesh.faces)
		for sl in [ self.slider_min , self.slider_max ]:
			sl.setMinimum( 0 )
			sl.setMaximum( mx )
			sl.setFocusPolicy(QtCore.Qt.StrongFocus)
			sl.setTickInterval(mx/10)
			sl.setSingleStep(1)
		self.slider_min.setValue(0)
		self.slider_min.setTickPosition(QtGui.QSlider.TicksAbove)
		self.slider_max.setTickPosition(QtGui.QSlider.TicksBelow)
		self.slider_max.setValue(mx)


class MeshWidget(QtOpenGL.QGLWidget):
	GL_MULTISAMPLE = 0x809D

	def initializeGL(self):
		# We call this right after our OpenGL window is created.
		glClearColor(1.0, 1.0, 1.0, 1.0)
		glClearDepth(1.0)
		glDepthFunc(GL_LESS)
		glEnable(GL_DEPTH_TEST)
		glShadeModel(GL_SMOOTH)

		glEnable(GL_NORMALIZE)
		light_position = (0., 0., 1., 0.)
		white_light = (1., 1., 1., 0.501)
		d_light = (1., 1., 1., 0.01)
		spec = (1., 1., 1., 0.08)
		glLightfv(GL_LIGHT0, GL_POSITION, light_position)
		glLightfv(GL_LIGHT0, GL_AMBIENT,  white_light)
		#glLightfv(GL_LIGHT0, GL_DIFFUSE,  d_light)
		glLightfv(GL_LIGHT0, GL_SPECULAR, spec)

		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)

		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
		#glBlendFunc(GL_SRC_ALPHA,GL_ONE)
		glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
		glEnable(GL_COLOR_MATERIAL)
		glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()

		gluPerspective(45.0, float(self.size().height())/
						float(self.size().width()), 0.1, 1000000.0)

		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		self.rotation = [0.0, 0.0]
		self.mesh.prepDraw()
		#glEnable(GL_CULL_FACE)

	def resizeGL(self, w, h):
		# Prevent A Divide By Zero If The Window Is Too Small
		h = max(1,h)
		glViewport(0, 0, w, h)

	def paintGL(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		h = self.size().height()
		w = self.size().width()
		glEnable(GL_DEPTH_TEST)
		glViewport(0, 0, w, h)
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
		glViewport(0, 0, w, h)
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
		self.rotation[0] -= sensitivity*(mouse_x-x)
		self.rotation[1] -= sensitivity*(mouse_y-y)
		self.prev_mouse = (x,y)
		self.update()
		event.accept()

	def __init__(self, parent,filename):
		super(MeshWidget,
				self).__init__(QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers),
													parent)
		self.setMinimumSize(640, 480)
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

	def reset(self):
		self.rotation=[0,0]
		self.prev_mouse = (0,0)
		self.zoom = -self.mesh.bounding_box.minViewDistance()
		self.update()


class MeshViewer(QtGui.QMainWindow):
	ESCAPE = '\033'

	def __init__(self,filename=None):
		QtGui.QMainWindow.__init__(self)
		self.filename = filename
		self.widget = MeshWidget(self,self.filename)
		self.bid_widget = BidPanel(self, self.widget.mesh)
		self.setCentralWidget(self.widget)
		self.cp = ControlPanel(self,self.bid_widget)
		self.cp.draw_bounding_box.setChecked( self.widget.draw_bounding_box )
		self.cp.draw_mesh.setChecked( self.widget.draw_mesh )
		cpDock = QtGui.QDockWidget("Control Panel", self)
		cpDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
								QtCore.Qt.RightDockWidgetArea)
		cpDock.setWidget(self.cp)
		self.addDockWidget(0x2,cpDock)

	def keyPressEvent(self, event):
		args = [event.text()]
		# If escape is pressed, kill everything.
		if args[0] == MeshViewer.ESCAPE:
			sys.exit()
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

	def setOptions(self):
		self.widget.draw_bounding_box = self.cp.draw_bounding_box.isChecked()
		self.widget.draw_mesh = self.cp.draw_mesh.isChecked()
		self.widget.update()

	def noise(self):
		for i in range(self.cp.iterationsSpinBox.value()):
			self.widget.mesh.noise( self.cp.lambdaSpinBox.value() )
			self.widget.update()

	def reload(self):
		self.widget.mesh.parse( self.filename )
		self.widget.mesh.prepDraw()
		self.widget.update()

	def save(self):
		self.filename = str(QtGui.QFileDialog.getSaveFileName(self,
							'Select file to save to'))
		self.filename = self.widget.mesh.write( self.filename )
		self.widget.update()

	def load(self):
		self.filename = str(QtGui.QFileDialog.getOpenFileName(self,
							'Select file to load'))
		self.reload()

	def enable_restrict(self):
		pass

	def set_restrict(self,k):
		self.widget.enable_restrict = self.cp.enable_restrict.isChecked()
		self.widget.restricted = range( self.cp.slider_min.value(),
									 self.cp.slider_max.value() )
		self.widget.update()
		print  self.cp.slider_min.value(), self.cp.slider_max.value()

	def saveScreenshot(self):
		filename = str(QtGui.QFileDialog.getSaveFileName(self,
							'Select file to save to'))
		h = self.widget.size().height()
		w = self.widget.size().width()
		screenshot = glReadPixels( 0,0, w, h, GL_RGBA, GL_UNSIGNED_BYTE)
		Image.frombuffer("RGBA", (w,h), screenshot,
							"raw", "RGBA", 0, 0).save(filename)

	def setPointDraw(self):
		self.widget.point_draw = self.cp.point_num.value()
		self.widget.update()
