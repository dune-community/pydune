#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
colors.py (c) 2009 rene.milk@uni-muenster.de
Licence: WTFPLv2, see LICENSE.txt
"""

from euclid import Vector3

constants = { 'black': Vector3(0,0,0), 'white':Vector3(255,255,255)}

def getHueVector( amount ):
	level = 0;
	while (1 << level) < amount:
		level += 1

	out = []
	return getHueVectorRec(out, amount, level)

def getHueVectorRec( out, amount, level ):
	if level <= 1:
		if len(out) < amount:
			out.append(0.0)
		if len(out) < amount:
			out.append(0.5)
		return out
	else:
		out = getHueVectorRec(out, amount, level - 1);
		lower = len(out)
		out = getHueVectorRec(out, amount, level - 1);
		upper = len(out)
		for i in range(lower,upper):
			out[i] += 1.0 / (1 << level)
		return out

def getColourPalette( size ):
	result = []#colors
	huevector = []#doubles
	satvalbifurcatepos = 0;
	satvalsplittings = []#doubles
	if len(satvalsplittings) == 0:
		#// insert ranges to bifurcate
		satvalsplittings.append( 1 )
		satvalsplittings.append( 0 )
		satvalbifurcatepos = 0

	huevector = getHueVector( size );
	bisectionlimit = 20;
	for i in range( len(result), size ):
		hue = huevector[i];
		saturation = 1;
		value = 1;
		switccolors = i % 3#; // why only 3 and not all combinations? because it's easy, plus the bisection limit cannot be divided integer by it

		if i % bisectionlimit == 0:
			satvalbifurcatepos = satvalbifurcatepos % ( len(satvalsplittings) -1 )
			toinsert = satvalbifurcatepos + 1
			satvalsplittings.insert( toinsert, ( satvalsplittings[satvalbifurcatepos] - satvalsplittings[satvalbifurcatepos + 1] ) / 2 + satvalsplittings[satvalbifurcatepos + 1] )
			satvalbifurcatepos += 2;

		if switccolors == 1:
			saturation = satvalsplittings[satvalbifurcatepos -1]
		elif switccolors == 2 :
			value = satvalsplittings[satvalbifurcatepos -1];

		hue += 0.17#; // use as starting point a zone where color band is narrow so that small variations means high change in visual effect
		if hue > 1:
			hue -= 1
		import colorsys
		col = colorsys.hsv_to_rgb( hue, saturation, value )
		result.append( col )
	return result

def getColourPaletteCheat( size, filter_colors=[] ):
	k = []
	org_size = size
	while len(k) < org_size:
		size += 1
		k = filter(lambda p: p not in filter_colors, set( getColourPalette( size ) ))
	return list(k)

if __name__ == '__main__':
	#k = getColourPalette( 9 )
	#print k
	#k = set(k)
	#print k
	print getColourPaletteCheat(4)
	print getColourPaletteCheat(4,[(0.0,0,0.0)])