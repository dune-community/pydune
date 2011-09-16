from util.meshutil import MeshVertexList

class SurfaceMesh(object):
	
	def __init__(self,dim):
		self.dim = dim
		self.vertex_list = MeshVertexList(self.dim)
		self.faces = []
		self.edges = []
		self.adj_points = dict()
		self.adj_faces = dict()
		self.refine = False
		
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

	def __repr__(self):
		return( '%dD surface mesh with %d vertices, %d edges and %d faces' %  
			(self.dim, len(self.vertex_list), len(self.edges),len(self.faces)))