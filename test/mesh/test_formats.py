
import dune.mesh.dgf as dgf
import dune.mesh.dgf.grammar as dgfgrammar
from dune.mesh import Mesh
import unittest
import os
import tempfile
import pyparsing

test = """DGF                        % comment
VERTEX                    % the vertices of the grid
0.000000    0.000000    0.000000    % vertex -1
1.949054    0.000000    0.000000    % vertex 0
#
SIMPLEX                    % the simplices of the grid
13    33    31    32    % simplex 0
32    10    0    30    % simplex 1
#
BOUNDARYSEGMENTS        % the boundary segments of the grid
2    10    11    25    % segment -1
2    10    0    11    % segment 0
#
#
BOUNDARYDOMAIN
default 1
#"""


class TestConvert(unittest.TestCase):
    grid_dir = os.path.join(os.path.dirname(__file__),"files")

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        print((self.tmpdir))

    def tearDown(self):
        #shutil.rmtree(self.tmpdir)
        pass

    def test_dgf(self):
        inst = dgf.grammar.instance()
        d = inst.parseString(test)
        m = Mesh(3)
        dgf.parse(m,d.dgf)
        d = inst.parseFile(os.path.join(self.grid_dir,
                                        'simplex.dgf'))
        m = Mesh(3)
        dgf.parse(m,d.dgf)

    def test_dgf_fail(self):
        inst = dgf.grammar.instance()
        with self.assertRaises(pyparsing.ParseException):
            inst.parseFile(os.path.join(self.grid_dir,'fail.dgf'))

if __name__ == '__main__':
    unittest.main()