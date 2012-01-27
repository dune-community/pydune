from mesh import Mesh
from util.meshutil import MeshVertexList

class SurfaceMesh(Mesh):
	
	def __init__(self,dim):
		super(SurfaceMesh,self).__init__(dim)


	def __repr__(self):
		return( '%dD surface mesh with %d vertices, %d edges and %d faces' %  
			(self.dim, len(self.vertex_list), len(self.edges),len(self.faces)))