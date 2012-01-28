#!/usr/bin/env python
"""
viewer.py (c) 2009 rene.milk@uni-muenster.de
Licence: WTFPLv2, see LICENSE.txt
"""

from PyQt4 import QtGui
from widgets import MeshViewer

usage = 'usage %s FILENAME'

def main(argv):
	app = QtGui.QApplication(['MeshViewer'])
	if len(argv) < 2 :
		print usage % argv[0]
	else:
		filename = argv[1]
		window = MeshViewer(filename)
		window.show()
		app.exec_()

