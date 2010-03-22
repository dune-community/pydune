#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
utils.py (c) 2009 rene.milk@uni-muenster.de,braindamage@springlobby.info

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
		k = set( getColourPalette( size ) )
	k = list(k)
	return filter(lambda p: p not in filter_colors,k)

if __name__ == '__main__':
	#k = getColourPalette( 9 )
	#print k
	#k = set(k)
	#print k
	print getColourPaletteCheat(4)
	print getColourPaletteCheat(4,[(0.0,0,0.0)])