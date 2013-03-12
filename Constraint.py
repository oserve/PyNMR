# Copyright Notice
# ================
# 
# The PyMOL Plugin source code in this file is copyrighted, but you can
# freely use and copy it as long as you don't change or remove any of
# the copyright notices.
# 
# ----------------------------------------------------------------------
#               This PyMOL Plugin is Copyright (C) 2013 by 
#                 olivier serve <olivier dot serve at gmail dot com>
# 
#                        All Rights Reserved
# 
# Permission to use, copy, modify, distribute, and distribute modified
# versions of this software and its documentation for any purpose and
# without fee is hereby granted, provided that the above copyright
# notice appear in all copies and that both the copyright notice and
# this permission notice appear in supporting documentation, and that
# the name(s) of the author(s) not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
# 
# THE AUTHOR(S) DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS.  IN
# NO EVENT SHALL THE AUTHOR(S) BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
# USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
# ----------------------------------------------------------------------
from AtomClass import AtomSet
from Geom import *

class Constraint(object):
	"""
	Abstract Constraint Class
	Contains informations about constraints
		atoms, model value, theoretical value,
		constraint number, constraint name
		and methods that allows to get these informations
		or to determine if the constraints is violated or not (TODO)
	"""
	
	def __init__(self):
		self.id = {}
		self.resis = []
		self.violated = ''
		self.definition = ''
		self.atoms = []
		self.constraintValues = {}
		self.numberOfAtomsSets = 0

	def setName(self,aName):
		self.id['name'] = aName

	def setConstraintValues(self, constraintValue, Vmin, Vplus):
		"""
		Set constraints values for violations
			determination
		"""
		self.constraintValues['constraint'] = float(constraintValue)
		self.constraintValues['min'] = float(Vmin)
		self.constraintValues['plus'] = float(Vplus)

	def isViolated(self):
		"""returns yes or no according to the violation state
		"""
		return self.violated

	def associatePDBAtoms(self):
		"""
		Sets atoms sets, checks for inconsistency with pdb file
		"""
		for atomsSetNumber in range(self.numberOfAtomsSets):
			self.atoms.append( AtomSet(self.pdbName, self.resis[atomsSetNumber]['number'], self.resis[atomsSetNumber]['atoms'] + self.resis[atomsSetNumber]['atoms_number']))

		return self.isValid()
	
	def isValid(self):
		"""
		"""
		validity=1
		for atomsSetNumber in range(self.numberOfAtomsSets):
			if "noID" in self.atoms[atomsSetNumber].getID():
				validity=0
				break
		return validity
