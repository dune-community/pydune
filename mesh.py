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

ply_header_tpl = """ply
format ascii 1.0
comment made by anonymous
comment this file is a cube
element vertex %d
property float32 x
property float32 y
property float32 z
element face %d
property list uint8 int32 vertex_index
end_header
"""

from gridhelper import *
from quadtree import Quadtree,Box
from euclid import *
import random
from OpenGL.GL import *
from OpenGL.GLU import *

def skipCommentsAndEmptyLines(fd):
	while fd:
		line = fd.readline()
		#if line.startswith( '#' ) or len(line) < 3:
		if line.startswith( '#' ):
			continue
		else:
			break
	return fd

def isAdjacentFace(fs,fa):
	for e in fs.edge_idx:
		e_ = ( e[1], e[0] )
		if e in fa.edge_idx or e_ in fa.edge_idx:
			return True
	return False

class Mesh():

	def __init__(self,dim):
		self.dim = dim
		self.draw_outline = True
		self.draw_faces = True
		self.outline_color = ( 1,1,1 )
		self.dl = None
		self.refine = False

	def parseSMESH(self, filename):
		PLCPointList.global_vertices = []
		self.vertices = PLCPointList(self.dim)
		self.faces = []
		self.edges = []
		self.adj_points = dict()
		self.adj_faces = dict()
		vert_fn_ = filename + '.vertices'
		face_fn_ = filename + '.faces'
		verts = open(vert_fn_, 'w')
		faces = open(face_fn_, 'w')
		fd = open( filename, 'r' )
		fd = skipCommentsAndEmptyLines( fd )
		print fd.readline()
		first = True
		while fd:
			line = fd.readline()
			if line.startswith( '#' ):
				continue
			if len(line.split()) < self.dim + 0:
				break
			if first:
				zero_based_idx = line.startswith('0')
				first = False
			verts.write(line)
		print 'vertice writing complete'
		#if zero_based_idx:
		fd = skipCommentsAndEmptyLines( fd )
		print fd.readline()
		while fd:
			line = fd.readline()
			if line.startswith( '#' ):
				continue
			if len(line.split()) < self.dim + 1:
				break
			faces.write(line)
		print 'face writing complete'
		verts.close()
		faces.close()
		self.parseSMESH_vertices(vert_fn_)
		print 'vert parsing complete'
		self.parseSMESH_faces(face_fn_, zero_based_idx)
		print 'face parsing complete'
		self.buildAdjacencyList()

	def parseSMESH_vertices(self,filename):
		fn = open( filename, 'r' )
		for line in fn.readlines():
			line = line.split()
			#this way I can use vector for either dim
			line.append(0)
			v = vector( line[1], line[2], line[3] )
			#use a dummy color
			self.vertices.appendVert( v, Vector3() )
		print 'read %d vertices'%len(self.vertices)
		fn.close()

	def parseSMESH_faces(self,filename,zero_based_idx,bidToColorMapper=BoundaryIdToColorMapper()):
		fn = open( filename, 'r' )
		for line in fn.readlines():
			line = line.split()
			#this way I can use vector for either dim
			line.append(0)
			if not zero_based_idx:
				v0 = int(line[1]) - 1
				v1 = int(line[2]) - 1
				v2 = int(line[3]) - 1
			else:
				v0 = int(line[1])
				v1 = int(line[2])
				v2 = int(line[3])
			b_id = int(line[4])
			if self.refine:
				d0 = self.vertices.verts[v0]
				d1 = self.vertices.verts[v1]
				d2 = self.vertices.verts[v2]
				c = (d0+d1+d2)/3.0
				c_id = self.vertices.appendVert( c )
				s0 = Simplex3(v0,v1,c_id,self.vertices,len(self.faces),b_id )
				self.faces.append( s0 )
				s1 = Simplex3(v1,v2,c_id,self.vertices,len(self.faces),b_id )
				self.faces.append( s1 )
				s2 = Simplex3(v2,v0,c_id,self.vertices,len(self.faces),b_id )
				self.faces.append( s2 )
			else:
				color = bidToColorMapper.getColor( b_id )
				s = Simplex3(v0,v1,v2,self.vertices,len(self.faces),color )
				self.faces.append( s )
				for v in [v0,v1,v2]:
					if self.adj_points.has_key(v) :
						self.adj_points[v] += [v0,v1,v2]
					else:
						self.adj_points[v] = [v0,v1,v2]
					self.adj_points[v].remove(v)
					if self.adj_faces.has_key(v):
						self.adj_faces[v].append( len(self.faces) - 1 )
					else:
						self.adj_faces[v] = [ len(self.faces) - 1 ]
		print 'read %d faces'%len(self.faces)
		fn.close()

	def buildAdjacencyList(self):
		self.adj = dict()
		i_s = 0
		for fs in self.faces:
			self.adj[i_s] = []
			for v in fs.idx:
				self.adj[i_s] += self.adj_faces[v]
			self.adj[i_s] = list(set(self.adj[i_s])) #remove double entries
			self.adj[i_s].remove(i_s)
			i_s += 1
			
	def drawFace(self, f,opacity=1.):
		glBegin(GL_POLYGON)					# Start Drawing The Pyramid
		n = f.n
		glNormal3f(n.x,n.y,n.z)
		for v in f.v:
			glColor4f(1.0,0,0,opacity)
			glVertex3f(v.x, v.y, v.z )
		glEnd()

	def drawOutline(self,f,opacity=1):
		glLineWidth(4)
		glBegin(GL_LINE_LOOP)
		n = f.n
		#glNormal3f(n.x,n.y,n.z)
		for v in f.v:
			glVertex3f(v.x, v.y, v.z )
		glEnd()
				
	def drawAdjacentFaces( self, face_idx ):
		for f_idx in self.adj[face_idx]:
			#self.drawOutline( self.faces[f_idx] )
			self.drawFace( self.faces[f_idx], 0.7 )
		#self.drawFace( self.faces[f_idx], 1.0 )
		self.drawOutline( self.faces[f_idx] )

	def draw(self, opacity=1.):
		glCallList(self.dl)

	def laplacianDisplacement(self,N_1_p,p):
		n = len( N_1_p )
		s = Vector3()
		if n > 0:
			for j in N_1_p:
				s += self.vertices.verts[j] - p
			s /= float(n)
		return s

	def scale(self,factor):
		for i,v in self.vertices.verts.iteritems():
			self.vertices.verts[i] *= factor
		self.prepDraw()

	def smooth(self,step):
		n = 0
		avg = 0.0
		for i,v in self.vertices.verts.iteritems():
			if self.adj_points.has_key(i):
				p_old = self.vertices.verts[i]
				displacement = step * self.laplacianDisplacement( self.adj_points[i], self.vertices.verts[i] )
				p_new = self.vertices.verts[i] + displacement
				self.vertices.verts[i] += displacement
				avg = ( abs(p_old)/abs(p_new) + n * avg ) / float( n + 1 )
				n += 1
		#self.scale( 0.91*avg )
		self.scale( 1.0*avg )
		self.prepDraw()

	def smooth2(self):
		n = 0
		avg = 0.0
		for f in self.faces:
			m = Vector3()
			area_sum = 0
			for f_n_id in self.adj[f.id]:
				f_n = self.faces[f_n_id]
				m += f_n.n * f_n.area
				area_sum += f_n.area
			m /= float(area_sum)
			self.faces[f_n_id].m = m / abs(m)
			displacement = [Vector3(),Vector3(),Vector3()]
			for i in range(3):
				p_old_i = f.v[i]
				area_n_sum = 0
				for t_id in self.adj_faces[f.idx[i]]:
					t = self.faces[t_id]
					area_n_sum += t.area
					v_t = (t.center - p_old_i).dot(t.m)*t.m
					displacement[i] += t.area * v_t
				displacement[i] /= area_n_sum
			for i in range(3):
				p_new = self.vertices.verts[f.idx[i]] + displacement[i]
				self.vertices.verts[f.idx[i]] = p_new
			#self.faces[f.id].reset(self.vertices)
		self.prepDraw()
		print 'smooth2 done'

	def noise(self,factor):
		for i,v in self.vertices.verts.iteritems():
			#self.vertices.verts[i] += random.gauss( factor, 1 ) * self.vertices.verts[i]
			self.vertices.verts[i] += random.random( ) * factor * self.vertices.verts[i]
		self.prepDraw()

	def prepDraw(self,opacity=1.):
		for f in self.faces:
			f.reset(self.vertices)
		if self.dl :
			glDeleteLists( self.dl, 1 )
		self.dl = glGenLists(1)
		self.bounding_box = BoundingVolume( self )
		self.quad = Quadtree(self)
		glNewList(self.dl,GL_COMPILE)
		if self.draw_faces:
			glBegin(GL_TRIANGLES)					# Start Drawing The Pyramid
			for f in self.faces:
				self.drawFace(f)
			glEnd()

		if self.draw_outline:
			for f in self.faces:
				glColor4f(0,0,0,opacity)
				self.drawOutline(f)
		glEndList()

	def drawFaceIdx(s,idx):
		f = s.faces[idx]
		s.drawFace(f)
		
	def drawFace(s,f):
		n = f.n
		glNormal3f(n.x,n.y,n.z)
		c = (f.color.x,f.color.y,f.color.z)
		glColor(c)
		for v in f.v:
			glVertex3f(v.x, v.y, v.z )

	def write(self,fn,bidMapper=ColorToBoundaryIdMapper()):
		out = None
		if not fn.endswith( '.smesh' ):
			fn += '.smesh'
		try:
			out = open(fn,'w')
		except:
			raise ImpossibleException()
		out.write( '#\n%d 3 0 %d\n'%(len(PLCPointList.global_vertices),3) )#3 bids
		out.write( '# all vertices\n#\n' )
		cVert = 1
		for v in PLCPointList.global_vertices:
				out.write( '%d %f %f %f\n'%(cVert,v.x,v.y,v.z) )
				cVert += 1

		out.write( '\n# number of facets (= number of triangles), border marker\n#\n%d 1\n'%(len(self.faces)) )
		out.write( '# all faces\n#\n' )
		
		for f in self.faces:
			assert isinstance( f, Simplex3 )
			out.write( '%d %d %d %d %d\n'%(3,f.idx[0],f.idx[1],f.idx[2],bidMapper.getID(f.color))  )

		out.write( '%d\n'%(0))

	def writePLY(self,fn):
		out = None
		if not fn.endswith( '.ply' ):
			fn += '.ply'
		try:
			out = open(fn,'w')
		except:
			raise ImpossibleException()
		out.write( ply_header_tpl%(len(PLCPointList.global_vertices),len(self.faces) ) ) 
		for v in PLCPointList.global_vertices:
				out.write( '%f %f %f\n'%(v.x,v.y,v.z) )

		for f in self.faces:
			assert isinstance( f, Simplex3 )
			out.write( '%d %d %d %d\n'%(3,f.idx[0],f.idx[1],f.idx[2])  )

		out.flush()
		out.close()

	def parsePLY(self,fn):
		fd = open( fn, 'r' )
		PLCPointList.global_vertices = []
		self.vertices = PLCPointList(self.dim)
		self.faces = []
		self.edges = []
		self.adj_points = dict()
		self.adj_faces = dict()
		num_verts = 0
		num_faces = 0
		#for line in fd.readlines():
		while fd:
			line = fd.readline()
			if line.startswith( 'end_header' ):
				break
			if line.startswith( 'element vertex' ):
				num_verts = int(line.split()[2])
				continue
			if line.startswith( 'element face' ):
				num_faces = int(line.split()[2])
				continue
		print 'read %d faces, %d vertices'%(num_faces,num_verts)
		for i in range(num_verts):
			line = fd.readline().split()
			try:
				v = vector( line[0], line[1], line[2] )
				if len(line) > 5:
					c = vector(line[3],line[4],line[5])
				else:
					c = Vector3()
				self.vertices.appendVert( v,c )
			except Exception, e:
				print e
				print line
				break
		for i in range(num_faces):
			line = fd.readline().split()
			v0 = int(line[1])
			v1 = int(line[2])
			v2 = int(line[3])
			s = Simplex3(v0,v1,v2,self.vertices,len(self.faces) )
			self.faces.append( s )
			for v in [v0,v1,v2]:
				if self.adj_points.has_key(v) :
					self.adj_points[v] += [v0,v1,v2]
				else:
					self.adj_points[v] = [v0,v1,v2]
				self.adj_points[v].remove(v)
				if self.adj_faces.has_key(v):
					self.adj_faces[v].append( len(self.faces) - 1 )
				else:
					self.adj_faces[v] = [ len(self.faces) - 1 ]

class BoundingVolume:
	def __init__(s,mesh):
		s.outline_color = ( 1,1,1 )
		vertices = mesh.vertices.verts.values()
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
			glVertex3f(v.x, v.y, v.z )
		glEnd()
		c = s.points
		glBegin(GL_LINES)
		
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
