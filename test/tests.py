#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
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

import sys
from PyQt4 import QtGui
from viewer import MeshViewer


def viewerTest(filename):
    app = QtGui.QApplication(['MeshViewer'])
    window = MeshViewer(filename)
    window.show()
    #app.exec_()

if __name__ == '__main__':
    do_diff = False
    if len(sys.argv) > 1:
        grids = sys.argv[1:]
    else:
        grids = ['test_grids/colored_aorta.ply','test_grids/tube.smesh',
             'test_grids/aorta_dune.smesh' ]
    for fn in grids:
        viewerTest(fn)