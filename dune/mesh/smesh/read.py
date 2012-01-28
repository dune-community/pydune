"""
read.py (c) 2010 rene.milk@uni-muenster.de
Licence: WTFPLv2, see LICENSE.txt
"""

try:
	#the spooled variant is new in 2.6
	from tempfile import SpooledTemporaryFile as TemporaryFile
except:
	from tempfile import TemporaryFile

from ..util.meshutil import ( MeshVertexList, 
	Simplex3, BoundaryIdToColorMapper, 
	ColorToBoundaryIdMapper, vector, find_key )
from ..util.euclid import Vector3,Vector2

def _skipCommentsAndEmptyLines(fd):
	while fd:
		line = fd.readline()
		if line.startswith( '#' ):
			continue
		else:
			break
	return fd

def _parseSMESH_vertices(self,fn):
	for line in fn.readlines():
		line = line.split()
		#this way I can use vector for either dim
		line.append(0)
		v = vector( line[1], line[2], line[3] )
		#use a dummy color
		self.vertex_list.addVertex( v, Vector3() )
	print 'read %d vertices'%len(self.vertex_list)

def _parseSMESH_faces(self,fn,bidToColorMapper=BoundaryIdToColorMapper()):
	for line in fn.readlines():
		line = line.split()
		if not self.zero_based_idx:
			v = map( lambda p: self.vertex_list.realIndex(int(p) -1 ), line[1:4] )
		else:
			v = map( lambda p: self.vertex_list.realIndex(int(p) ), line[1:4] )
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
			s = Simplex3(v[0],v[1],v[2],self.vertex_list,len(self.faces),color, boundary_id )
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


def parseSMESH(self, filename):
	vert_fn_ = filename + '.vertices'
	face_fn_ = filename + '.faces'
	verts = TemporaryFile(mode='w+r')
	faces = TemporaryFile(mode='w+r')
	fd = open( filename, 'r' )
	fd = _skipCommentsAndEmptyLines( fd )
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

	fd = _skipCommentsAndEmptyLines( fd )
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
	_parseSMESH_vertices(self,verts)
	print 'vert parsing complete'
	_parseSMESH_faces(self, faces)
	print 'face parsing complete'
	self.buildAdjacencyList()
