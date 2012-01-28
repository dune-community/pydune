import sys
from distutils.core import setup

setup(
    name='pyDune',
    version='0.1.0',
    author='Rene Milk',
    author_email='rene.milk@uni-muenster.de',
    packages=['dune', 'dune.mesh', 'dune.mesh.gui', 'dune.mesh.dgf', 'dune.mesh.smesh', 
	    'dune.mesh.util', 'dune.mesh.converter', 'dune.mesh.generator'],
    scripts=['bin/%s'%n for n in ['mesh-convert', 'mesh-generate', 'mesh-viewer', 'tetgen2dgf', 'triangle2dgf'] ]
    url='http://pypi.python.org/pypi/pydune/',
    license='LICENSE.txt',
    description='spring content downloading',
    long_description=open('README.txt').read(),
    # running `setup.py sdist' gives a warning about this, but still
    # install_requires is the only thing that works with pip/easy_install...
    install_requires=['matplotlib', 'pyparsing', 'PyQt', 'nose-cov', 'nosetest']
)
