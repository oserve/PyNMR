from Constraint import Constraint

class ConstraintSetManager(object):
	"""Class to manage a set of constraints
	"""
	def __init__(self, managerName):
		self.constraints = []
		self.residuesList = []
		self.pdb = ''
		self.name=managerName

	#Constraints management methods

	def setPDB(self, pdb):
		"""Sets the name of the structure (usually a PDB File) on which the distance should be calculated
		"""
		self.pdb = pdb
		if len(self.constraints):
			for constraint in self.constraints:
				constraint.pdbName = self.pdb

	def associateToPDB(self):
		"""Invokes associatePDBAtoms function on all constraints
		"""
		result=0
		if self.pdb <> '':
			if len(self.constraints):
				for constraint in self.constraints:
					constraint.associatePDBAtoms()
					result=1
		return result

	def removeAllConstraints(self):
		"""Empties an array of constraints
		"""
		while len(self.constraints) > 0:
			for constraint in self.constraints:
				constraintsSet.remove(constraint)

	def addConstraint(self, aConstraint):
		"""Add a constraint to the constraint list of the manager and update the list of residues
		"""
		self.constraints.append(aConstraint)
		aConstraint.setName(self.name)
		for resiNumber in aConstraint.getResisNumber():
			if resiNumber not in self.residuesList:
				self.residuesList.append(resiNumber)

	def removeConstraint(self, aConstraintNumber):
		"""
		"""
		if int(aConstraintNumber) in self.constraints.keys():
			del self.constraints[int(aConstraintNumber)]