#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
mesh.py (c) 2010 rene.milk@uni-muenster.de
Licence: WTFPLv2, see LICENSE.txt
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

from util.meshutil import MeshVertexList, Simplex3, BoundaryIdToColorMapper, \
	ColorToBoundaryIdMapper, vector, find_key
from gui.quadtree import Quadtree,Box
from util.euclid import Vector3
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from gui.bounding import BoundingVolume
from collections import defaultdict
import smesh

try:
	#the spooled variant is new in 2.6
	from tempfile import SpooledTemporaryFile as TemporaryFile
except:
	from tempfile import TemporaryFile


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
		self.bid_color_mapping = defaultdict(list)
		self.vertex_list = MeshVertexList(self.dim)
		self.faces = []
		self.edges = []
		self.adj_points = dict()
		self.adj_faces = dict()
		
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
			
# ---------------Parsing--------------------------------------------------------------------------------- #

	def parse(self, filename):
		self.faces = []
		self.edges = []
		self.adj_points = dict()
		self.adj_faces = dict()
		num_verts = 0
		num_faces = 0
		self.vertex_list = MeshVertexList(self.dim)
		if filename.endswith( '.ply' ):
			self.parsePLY( filename )
		else:
			smesh.read( self, filename )
		self.bid_color_mapping = defaultdict(list)
		for f in self.faces:
			self.bid_color_mapping[f.boundary_id].append(f.color)

	def parsePLY(self,fn):
		color_mapper = ColorToBoundaryIdMapper()
		fd = open( fn, 'r' )
		#a rather hard assumption...
		self.zero_based_idx = True
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
		for i in range(num_faces):
			line = map( lambda p: self.vertex_list.realIndex(int(p)), fd.readline().split()[1:] )
			v0 = line[0]
			v1 = line[1]
			v2 = line[2]
			s = Simplex3(v0,v1,v2,self.vertex_list,len(self.faces),None, color_mapper.getID( self.vertex_list.attribs[v0] ) )
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

		#we store a running avg normal per bid
		normals = dict()
		for f in self.faces:
			assert isinstance( f, Simplex3 )
			boundary_id = bidMapper.getID(f.color)
			if normals.has_key( boundary_id ):
				i,n = normals[boundary_id]
				normals[boundary_id] = (i+1, ( n * i + f.n )/(i+1) )
			else:
				normals[boundary_id] = (1, f.n )
			out.write( '%d %d %d %d %d\n'%(3,f.idx[0],f.idx[1],f.idx[2], boundary_id ) )
		out.write( '%d\n'%(0))
		out.close()
		normals_file = open( fn + '.normals' ,'w')
		for i,n in normals.iteritems():
			#for m in [n[1],n[1]/abs(n[1])]:
			m = n[1]
			normals_file.write( 'gd_%d: %f;%f;%f\n'%(i,m.x,m.y,m.z) )
		normals_file.close()
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
			idx = map( lambda p: p + 1, f.idx )
			out.write( '%d %d %d %d\n'%(3,idx[0],idx[1],idx[2])  )

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
		glColor3fv(f.color())
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

	def equals(self,other):
		lists = ['faces', 'edges']
		for l in lists:
			diff = set(getattr(self,l)) ^ set(getattr(other,l))
			if len(diff) > 0:
				return False