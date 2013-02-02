#
#  Constraint.py
#
#
#  Created by olivier on 16/05/09.
#  Copyright (c) 2009 ICSN. All rights reserved.
#
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
