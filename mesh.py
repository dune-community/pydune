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
element vertex %d
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
element face %d
property list uchar uint vertex_index
end_header
"""

from meshutil import MeshVertexList, Simplex3, BoundaryIdToColorMapper, \
	ColorToBoundaryIdMapper, vector, find_key
from quadtree import Quadtree,Box
from euclid import Vector3
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from bounding import BoundingVolume
#from meshutil import *

try:
	#the spooled variant is new in 2.6
	from tempfile import SpooledTemporaryFile as TemporaryFile
except:
	from tempfile import TemporaryFile

def skipCommentsAndEmptyLines(fd):
	while fd:
		line = fd.readline()
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

# ---------------Parsing--------------------------------------------------------------------------------- #

	def parse(self, filename):
		if filename.endswith( '.ply' ):
			self.parsePLY( filename )
		else:
			self.parseSMESH( filename )

	def parseSMESH(self, filename):
		self.vertex_list = MeshVertexList(self.dim)
		self.faces = []
		self.edges = []
		self.adj_points = dict()
		self.adj_faces = dict()
		vert_fn_ = filename + '.vertices'
		face_fn_ = filename + '.faces'
		verts = TemporaryFile(mode='w+r')
		faces = TemporaryFile(mode='w+r')
		fd = open( filename, 'r' )
		fd = skipCommentsAndEmptyLines( fd )
		#skip one more line..
		dummy = fd.readline()
		first_vert = True
		while fd:
			line = fd.readline()
			if line.startswith( '#' ):
				continue
			if len(line.split()) < self.dim + 0:
				break
			if first_vert:
				self.zero_based_idx = line.startswith('0')
				first_vert = False
			verts.write(line)
		print 'vertice writing complete'

		fd = skipCommentsAndEmptyLines( fd )
		#skip one more line..
		dummy = fd.readline()
		while fd:
			line = fd.readline()
			if line.startswith( '#' ):
				continue
			if len(line.split()) < self.dim + 1:
				break
			faces.write(line)
		print 'face writing complete'

		#we need the cursor at top for individual parsing
		verts.seek(0)
		faces.seek(0)
		self.parseSMESH_vertices( verts )
		print 'vert parsing complete'
		self.parseSMESH_faces( faces )
		print 'face parsing complete'
		self.buildAdjacencyList()

	def parseSMESH_vertices(self,fn):
		for line in fn.readlines():
			line = line.split()
			#this way I can use vector for either dim
			line.append(0)
			v = vector( line[1], line[2], line[3] )
			#use a dummy color
			self.vertex_list.addVertex( v, Vector3() )
		print 'read %d vertices'%len(self.vertex_list)

	def parseSMESH_faces(self,fn,bidToColorMapper=BoundaryIdToColorMapper()):
		for line in fn.readlines():
			line = line.split()
			#if not self.zero_based_idx:
				#v = map( lambda p: self.vertex_list.realIndex(int(p) -1 ), line[1:4] )
			#else:
				#v = map( lambda p: self.vertex_list.realIndex(int(p) ), line[1:4] )
			line.append(0)
			if not self.zero_based_idx:
				v0 = int(line[1]) - 1
				v1 = int(line[2]) - 1
				v2 = int(line[3]) - 1
				#v = map( lambda p: self.vertex_list.realIndex(int(p) -1 ), line[1:4] )
			else:
				v0 = int(line[1])
				v1 = int(line[2])
				v2 = int(line[3])
			v = [v0,v1,v2]
			boundary_id = int(line[4])
			color = bidToColorMapper.getColor( boundary_id )
			if self.refine:
				assert False
				d0 = self.vertex_list.verts[v0]
				d1 = self.vertex_list.verts[v1]
				d2 = self.vertex_list.verts[v2]
				c = (d0+d1+d2)/3.0
				c_id = self.vertex_list.addVertex( c, color )
				s0 = Simplex3(v0,v1,c_id,self.vertex_list,len(self.faces),boundary_id )
				self.faces.append( s0 )
				s1 = Simplex3(v1,v2,c_id,self.vertex_list,len(self.faces),boundary_id )
				self.faces.append( s1 )
				s2 = Simplex3(v2,v0,c_id,self.vertex_list,len(self.faces),boundary_id )
				self.faces.append( s2 )
			else:
				s = Simplex3(v[0],v[1],v[2],self.vertex_list,len(self.faces),color )
				self.faces.append( s )
				for one_v in v:
					if self.adj_points.has_key(one_v) :
						self.adj_points[one_v] = self.adj_points[one_v].union( set(v) )
					else:
						self.adj_points[one_v] = set(v)

					if self.adj_faces.has_key(one_v):
						self.adj_faces[one_v].append( len(self.faces) - 1 )
					else:
						self.adj_faces[one_v] = [ len(self.faces) - 1 ]
		print 'read %d faces'%len(self.faces)

	def parsePLY(self,fn):
		fd = open( fn, 'r' )
		#a rather hard assumption...
		self.zero_based_idx = True
		self.vertex_list = MeshVertexList(self.dim)
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
				self.vertex_list.addVertex( v,c )
			except Exception, e:
				print e
				print line
				raise e
		#print len(self.vertex_list.duplicates),self.vertex_list.duplicates
		print filter( lambda (i,v): i != v, self.vertex_list.aliases.iteritems() )
		for i in range(num_faces):
			line = map( lambda p: self.vertex_list.realIndex(int(p)), fd.readline().split()[1:] )
			v0 = line[0]
			v1 = line[1]
			v2 = line[2]
			s = Simplex3(v0,v1,v2,self.vertex_list,len(self.faces) )
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

	def buildAdjacencyList(self):
		self.adj = dict()
		i_s = 0
		for face in self.faces:
			self.adj[i_s] = []
			for v in face.idx:
				self.adj[i_s] += self.adj_faces[v]
			#remove duplicate entries
			self.adj[i_s] = list(set(self.adj[i_s]))
			self.adj[i_s].remove(i_s)
			i_s += 1

# --------Writing---------------------------------------------------------------------------------------- #

	def write(self,fn,bidMapper=ColorToBoundaryIdMapper()):
		if fn.endswith( '.ply' ):
			return self.writePLY( fn )
		else:
			return self.writeSMESH( fn, bidMapper )

	def writeSMESH(self,fn,bidMapper=ColorToBoundaryIdMapper()):
		out = None
		if not fn.endswith( '.smesh' ):
			fn += '.smesh'
		try:
			out = open(fn,'w')
		except:
			raise ImpossibleException()
		out.write( '#\n%d 3 0 %d\n'%(len(self.vertex_list),3) )#3 bids
		out.write( '# all vertices\n#\n' )
		cVert = int(not self.zero_based_idx)
		for i in range( len(self.vertex_list) ):
			v = self.vertex_list[i]
			out.write( '%d %f %f %f\n'%(cVert,v.x,v.y,v.z) )
			cVert += 1

		out.write( '\n# number of facets (= number of triangles), border marker\n#\n%d 1\n'%(len(self.faces)) )
		out.write( '# all faces\n#\n' )

		for f in self.faces:
			assert isinstance( f, Simplex3 )
			out.write( '%d %d %d %d %d\n'%(3,f.idx[0],f.idx[1],f.idx[2],bidMapper.getID(f.color))  )

		out.write( '%d\n'%(0))
		out.close()
		return fn

	def writePLY(self,fn):
		out = None
		if not fn.endswith( '.ply' ):
			fn += '.ply'
		try:
			out = open(fn,'w')
		except:
			raise ImpossibleException()
		out.write( ply_header_tpl%(len(self.vertex_list),len(self.faces) ) )
		for i in range( len(self.vertex_list) ):
				v = self.vertex_list[i]
				c = self.vertex_list.attribs[i]
				#this will generate all black vertices, but conforms to format
				out.write( '%f %f %f %d %d %d\n'%(v.x,v.y,v.z,c.x,c.y,c.z ) )

		for f in self.faces:
			assert isinstance( f, Simplex3 )
			out.write( '%d %d %d %d\n'%(3,f.idx[0],f.idx[1],f.idx[2])  )

		out.flush()
		out.close()
		return fn

# ----------Drawing-------------------------------------------------------------------------------------- #

	def drawOutline(self,f,opacity=1):
		glLineWidth(2)
		glBegin(GL_LINE_LOOP)
		glNormal3fv(f.n())
		for v in f.v:
			glVertex(v())
		glEnd()
				
	def drawAdjacentFaces( self, face_idx ):
		for f_idx in self.adj[face_idx]:
			#self.drawOutline( self.faces[f_idx] )
			self.drawFace( self.faces[f_idx], 0.7 )
		#self.drawFace( self.faces[f_idx], 1.0 )
		self.drawOutline( self.faces[f_idx] )

	def draw(self, opacity=1.):
		glCallList(self.dl)

	def prepDraw(self,opacity=1.):
		for f in self.faces:
			f.reset(self.vertex_list)
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
		glNormal3fv(f.n())
		glColor(f.color())
		for v in f.v:
			glVertex(v())

# ----------Mesh deformation-------------------------------------------------------------------------------------- #

	def laplacianDisplacement(self,N_1_p,p):
		n = len( N_1_p )
		s = Vector3()
		if n > 0:
			for j in N_1_p:
				s += self.vertex_list[j] - p
			s /= float(n)
		return s

	def scale(self,factor):
		for i in range(len(self.vertex_list)):
			self.vertex_list[i] *= factor
		self.prepDraw()

	def smooth(self,step):
		n = 0
		avg = 0.0
		for i in range( len(self.vertex_list) ):
			if self.adj_points.has_key(i):
				p_old = self.vertex_list[i]
				displacement = step * self.laplacianDisplacement( self.adj_points[i], self.vertex_list[i] )
				p_new = self.vertex_list[i] + displacement
				self.vertex_list[i] += displacement
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
				p_new = self.vertex_list[f.idx[i]] + displacement[i]
				self.vertex_list[f.idx[i]] = p_new
			#self.faces[f.id].reset(self.vertex_list)
		self.prepDraw()
		print 'smooth2 done'

	def noise(self,factor):
		for i in range( len(self.vertex_list) ):
			#self.vertex_list.verts[i] += random.gauss( factor, 1 ) * self.vertex_list.verts[i]
			self.vertex_list.verts[i] += random.random( ) * factor * self.vertex_list.verts[i]
		self.prepDraw()