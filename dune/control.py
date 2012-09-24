#!/usr/bin/env python

import tempfile
import os
import random
import string
import subprocess

class Dunecontrol(object):
	def __init__(self,script_path):
		self._script_path = script_path
		self._base_dir = os.path.join(os.path.dirname(script_path), '../..')

	def _call(self, args):
		try:
			cl = [self._script_path] + args
		except:
			cl = [self._script_path] + args.split()
		return subprocess.check_output(cl, cwd=self._base_dir,stderr=subprocess.STDOUT)

	def printdeps(self, module):
		import pprint
		pprint.pprint(self.dependencies(module))

	def dependencies(self, module):
		out = self._call(['--module=%s'%module, 'printdeps']).split('\n')[1:]
		def cleanup(name):
			return m.split()[0].strip().replace('_', '-')
		required = [cleanup(m) for m in out if 'required' in m ]
		suggested = [cleanup(m) for m in out if 'suggested' in m ]
		return {'required':required, 'suggested': suggested}

	def configure(self,module=None):
		return self._call(['--module=%s'%module,'configure']).split()

	def autogen(self,module=None):
		return self._call(['--module=%s'%module,'autogen']).split()

	def make(self,module=None):
		return self._call(['--module=%s'%module,'make']).split()

if __name__ == "__main__":
	p = '/home/r_milk01/projekte/uni/dune/multiscale-super/dune-common/bin/dunecontrol'
	ctrl = Dunecontrol(p)
	print ctrl.printdeps('dune-stuff')
	
