#!/usr/bin/env python3

import os
import sys
from dune.control import Dunecontrol

modules = ['dune-common', 'dune-geometry', 'dune-localfunctions', 'dune-grid', 'dune-istl',
           'dune-python', 'dune-testtools', 'dune-functions', 'dune-alugrid', 'dune-fem',
           'dune-typetree', 'dune-pdelab', 'dune-grid-glue', 'dune-pybindxi', 'dune-uggrid',
           'dune-xt-common', 'dune-xt-functions', 'dune-xt-grid', 'dune-xt-la']
modules = ['dune-common', 'dune-geometry', 'dune-localfunctions', 'dune-grid', 'dune-istl']

basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
control = Dunecontrol(os.path.join(basepath, 'dune-common', 'bin', 'dunecontrol'))

with open('CMakeLists.txt', 'wt') as out:
    out.write('''project(dune-xt-super)
set(CMAKE_INSTALL_PREFIX /tmp/t1/install)
set(CMAKE_PREFIX_PATH /tmp/t1/prefix)
include(${CMAKE_ROOT}/Modules/ExternalProject.cmake)''')
    for mod in modules:
        all_deps = control.dependencies(mod)
        deps = '" "'.join(all_deps['required'])
        sec = '''
ExternalProject_Add({mod} 
                    SOURCE_DIR ${{CMAKE_CURRENT_SOURCE_DIR}}/{mod}
                    DOWNLOAD_COMMAND ""
                    UPDATE_COMMAND ""
                    DEPENDS "{deps}"
                    CMAKE_ARGS -DCMAKE_INSTALL_PREFIX=/tmp/t1/install
                    )
'''
        out.write(sec.format(mod=mod, deps=deps))

#print(open('CMakeLists.txt', 'rt').read())