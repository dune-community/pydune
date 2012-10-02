import sys
from distutils.core import setup

setup(
    name = 'pyDune',
    version = '0.1.3a',
    author = 'Rene Milk',
    author_email = 'rene.milk@uni-muenster.de',
    packages = ['dune', 'dune.mesh', 'dune.mesh.gui', 'dune.mesh.dgf', 'dune.mesh.smesh',
        'dune.mesh.util', 'dune.mesh.converter', 'dune.mesh.generators'],
    scripts = ['bin/%s'%n for n in ['mesh-convert', 'mesh-generate', 'mesh-viewer', 'tetgen2dgf', 'triangle2dgf', 'dune-supermodule'] ],
    url = 'http://users.dune-project.org/projects/pydune',
    description = 'assorrted DUNE related scripts and utilities',
    long_description = open('README.txt').read(),
    # running `setup.py sdist' gives a warning about this, but still
    # install_requires is the only thing that works with pip/easy_install...
    # we do not list pyqt here since pip can't seem to install it
    install_requires = ['matplotlib', 'pyparsing', 'nose-cov', 'nose', 'nosehtmloutput', 'rednose', 'GitPython'],
    classifiers = ['Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Visualization'],
    license = 'LICENSE.txt'
)
