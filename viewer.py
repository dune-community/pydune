#!/usr/bin/env python
"""
de
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

from PyQt4 import QtGui
from widgets import MeshViewer
import sys

usage = 'usage %s FILENAME'

if __name__ == '__main__':
	app = QtGui.QApplication(['MeshViewer'])
	if len(sys.argv) < 2 :
		print usage%sys.argv[0]
	else:
		filename = sys.argv[1]
		window = MeshViewer( filename )
		window.show()
		app.exec_()

