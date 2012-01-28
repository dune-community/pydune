test = """DGF						% comment
VERTEX					% the vertices of the grid
0.000000	0.000000	0.000000	% vertex -1
1.949054	0.000000	0.000000	% vertex 0
#
SIMPLEX					% the simplices of the grid
13	33	31	32	% simplex 0
32	10	0	30	% simplex 1
#
BOUNDARYSEGMENTS		% the boundary segments of the grid
2	10	11	25	% segment -1
2	10	0	11	% segment 0
#
#
BOUNDARYDOMAIN
default 1
#"""

import dune.mesh.dgf.grammar

class TestConvert(unittest.TestCase):
	grid_dir = os.path.join(os.path.dirname(__file__),"files")

	def setUp(self):
		self.tmpdir = tempfile.mkdtemp()
		print(self.tmpdir)

	def tearDown(self):
		#shutil.rmtree(self.tmpdir)
		pass

	def test_dgf(self):
		#d = dgf.parseString(test)
		d = grammar.instance().parseFile('out.dgf')
		#print d
		#not actually a surface mesh...
		m = Mesh(3)
		#pprint.pprint(d.asDict())
		#pprint.pprint(d)
		parse(m,d.dgf)
		print m
		print d.dgf.asXML()
			#for s in d.dgf:
				#print s.getName()
				#for e in s:
					#print e.getName()

if __name__ == '__main__':
	unittest.main()