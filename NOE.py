from sys import stderr
from Constraint import Constraint
from Geom import centerOfMass, calcDistance

class NOE(Constraint):
	"""
	NOE inherits from Constraint
	Contains additional methods specific to NOE constraint
	"""
	
	def __init__(self):
		super(NOE, self).__init__()
		self.points = {}
		self.numberOfAtomsSets = 2		

	def setViolationState(self, cutOff):
		"""Set violation state, with optional additional cutoff
		"""
		if (self.constraintValues['actual'] <= (self.constraintValues['constraint']-self.constraintValues['min']-cutOff)):
			self.violated = 'violated'
			self.constraintValues['closeness'] = 'tooClose'
		elif (self.constraintValues['actual'] >= (self.constraintValues['constraint'] + self.constraintValues['plus'] + cutOff)):
			self.violated = 'violated'
			self.constraintValues['closeness'] = 'tooFar'
		else:
			self.violated = 'not violated'

	def getRange(self):
		if not (int(self.resis[0]['number'])-int(self.resis[1]['number'])):
			return 'intra'
		elif abs(int(self.resis[0]['number'])-int(self.resis[1]['number'])) == 1:
			return 'sequential'
		elif abs(int(self.resis[0]['number'])-int(self.resis[1]['number'])) > 1 and abs(int(self.resis[0]['number'])-int(self.resis[1]['number'])) <= 5:
			return 'medium'
		elif abs(int(self.resis[0]['number'])-int(self.resis[1]['number'])) > 5:
			return 'long'
		else:
			stderr.write('How come ?\n')

	def getID(self):
		"""Returns name of constraints : Name_(constraint number)_(pdbName)_(violation_state)
		"""
		if self.violated <> '':
			if self.violated == 'violated':
				return self.id['name'] + str(self.id['number']) + "_V" + "_" + self.pdbName
			else:
				return self.id['name'] + str(self.id['number']) + "_NV" + "_" + self.pdbName
		else:
			stderr.write("Can not give ID : Violation state not defined for constraint : " + self.pdbName + "_" + self.id['name'] + str(self.id['number']) + "\n" + self.printCons() + "\n")

	def setDistance(self, method):
		"""Set actual distance of the constraint in the current pdb file
		"""
		self.points[0] = centerOfMass(self.atoms[0].getID())
		self.points[1] = centerOfMass(self.atoms[1].getID())
		self.constraintValues['actual'] = calcDistance(self.atoms[0].getID(), self.atoms[1].getID(), method)
		if self.constraintValues['actual'] <= 0:
			return 0
		else:
			return 1

	def getResisNumber(self):
		"""
		"""
		return [self.resis[0]['number'],self.resis[1]['number']]

