#!/usr/bin/env python
from pyparsing import ( Optional, oneOf, 
	Dict, Literal, Word, printables, Group, 
	OneOrMore, ZeroOrMore, FollowedBy, Keyword,
	Suppress,LineEnd, White,alphanums,alphas,
	CaselessLiteral, Combine, nums, Or,
	srange, Regex)

point = Literal('.')
e = CaselessLiteral('E')
plusorminus = Literal('+') | Literal('-')
number = Word(nums) 
integer = Combine( Optional(plusorminus) + number )
floatnumber = Combine( integer +
                       Optional( point + Optional(number) ) +
                       Optional( e + integer )
                     )

#comment = Suppress("%") + Word(alphanums + " ") 
comment = Regex(r"%.*").setName("comment").suppress()
linend = Or( [comment , LineEnd()] ).suppress()
vertex = (Group( OneOrMore( floatnumber('point') + OneOrMore( White() ).suppress() ) ) + linend)('vertex')
vertices_header = (Keyword('VERTEX') + linend).suppress()
section_end = (Literal('#') + LineEnd()).suppress()
vertices = (vertices_header.suppress() + Group(OneOrMore( vertex )) + section_end)('vertices')
begin = (Keyword('DGF') + linend).suppress()
end = Literal('#').suppress() #+ White() + Literal('#')
dgf = (begin + OneOrMore( vertices ) + OneOrMore( section_end ))('dgf')

test = """DGF
VERTEX % dew
0.000000	0.000000	0.000000	% vertex -1
1.949054	0.000000	0.000000	% vertex 0
#
#"""
d = dgf.parseString(test)
print d.asXML()
#p = dgf.parseFile('out.dgf')
#print p