#
#  ConstraintsDrawing.py
#  
#
#  Created by olivier on 16/05/09.
#  Copyright (c) 2009 ICSN. All rights reserved.
#
#Module for drawing constraints
from sys import stderr, stdout
from MolecularViewerInterface import setBfactor, drawConstraint, paintDensity, zeroBFactors
from ConstraintManager import ConstraintSetManager

class ConstraintDrawer(object):
	"""

	"""
	def drC(self, selectedConstraint, radius, colors):
		"""
		Draw an array of constraints according to the filter defined by user, using the drawConstraint function
		"""	
		involvedResidueslist = []
		numberOfDrawnConstraints = 0
		for aConstraint in selectedConstraint:
			if not aConstraint.resis[0]['number'] in involvedResidueslist:
				involvedResidueslist.append(aConstraint.resis[0]['number'])
			if not aConstraint.resis[1]['number'] in involvedResidueslist:
				involvedResidueslist.append(aConstraint.resis[1]['number'])
			if aConstraint.violated == 'violated':
				color = colors[aConstraint.constraintValues['closeness']]
			elif aConstraint.violated == 'not violated':
				color = colors['notViolated']
			drawConstraint(aConstraint.points, color, radius, aConstraint.getID())
			numberOfDrawnConstraints = numberOfDrawnConstraints + 1
		return {'Residueslist':involvedResidueslist, 'DrawnConstraints':numberOfDrawnConstraints}

	def constraintsDensity(self, selectedConstraints):
		"""Calculate number of constraints per residue for selected constraints by the filter
		"""
		list = {}
		constraintsUsed = 0
		for aConstraint in selectedConstraints:
			if not aConstraint.resis[0]['number'] in list.keys():
				list[aConstraint.resis[0]['number']] = 10
			else:
				list[aConstraint.resis[0]['number']] = list[aConstraint.resis[0]['number']] + 10
			if not aConstraint.resis[1]['number'] in list.keys():
				list[aConstraint.resis[1]['number']] = 10
			else:
				list[aConstraint.resis[1]['number']] = list[aConstraint.resis[1]['number']] + 10
			constraintsUsed = constraintsUsed + 1
		return list

	def paD(self, selectedConstraints, pdb, color_gradient):
		"""Uses b-factors to simulate constraint density on structure
		"""
		densityList = self.constraintsDensity(selectedConstraints)
		zeroBFactors(pdb)
		if len(densityList) > 0:
			for residu in densityList.keys():
				setBfactor(pdb + " & i. " + residu, densityList[residu])
		paintDensity(color_gradient, pdb)
		return densityList
