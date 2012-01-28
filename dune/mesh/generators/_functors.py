"""
grammar.py (c) 2011 rene.milk@uni-muenster.de
Licence: WTFPLv2, see LICENSE.txt
"""

import math

class IFunctor:
	def scale(self, x):
		raise NotImplementedException()
	
class HyperboleFunctorZ(IFunctor):
	def __init__(self,tube_length,fac,additive):
		self.tube_length	= tube_length
		self.fac 			= fac
		self.additive		= additive
	
	def scale(self, x):
		mult = self.fac
		#if x.z != self.tube_length:
		mult *= (self.tube_length - x.z) / float( self.tube_length + x.z ) + self.additive
		x.x *= mult
		x.y *= mult
		return x
	
class IdentityFunctor(IFunctor):
	def scale(self, x):
		return x
	