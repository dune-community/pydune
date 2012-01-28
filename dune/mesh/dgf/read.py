#!/usr/bin/env python
"""
read.py (c) 2011 rene.milk@uni-muenster.de
Licence: WTFPLv2, see LICENSE.txt
"""

from ..util.meshutil import (Simplex3,
	BoundaryIdToColorMapper)
from ..util.euclid import Vector3, Vector2
from ..util import colors
		
def parse(mesh, dgf):
	for vertex in dgf.vertices:
		if mesh.dim == 2:
			vert = Vector2(vertex[0], vertex[1])
		else:
			vert = Vector3(vertex[0], vertex[1], vertex[2])
		mesh.vertex_list.addVertex(vert, colors.constants['white'])
	bid_color_mapper = BoundaryIdToColorMapper()
	for vert in dgf.boundarysegments:
		color = bid_color_mapper.getColor(vert[0])
		simplex = Simplex3(vert[1], vert[2], vert[3], mesh.vertex_list, 
					len(mesh.faces), color, vert[0] )
		mesh.faces.append(simplex)
