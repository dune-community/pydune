# Author: Tobi Vollebregt
#
# Makefile for development purposes.
#

.PHONY: all pylint test

all: README.txt README.html

# PyPI wants ReStructured text
README.txt: README.markdown
	pandoc -f markdown -t rst $< > $@

# I want HTML (to preview the formatting :))
README.html: README.markdown
	pandoc -f markdown -t html $< > $@

pylint:
	pylint dune

test:
	py.test test
	check-manifest

doc:
	sphinx-build docs _build
