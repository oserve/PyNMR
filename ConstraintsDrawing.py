#
#  ConstraintsDrawing.py
#  
#
#  Created by olivier on 16/05/09.
#  Copyright (c) 2009 ICSN. All rights reserved.
#
#Module for drawing constraints
from sys import stderr, stdout
import time
from MolecularViewerInterface import setBfactor, drawConstraint, paintDensity, zeroBFactors
from ConstraintManager import ConstraintSetManager

class ConstraintDrawer(object):
	"""

	"""

	def drC(self, aConstraintManager, aFilter, radius, colors):
		"""
		Draw an array of constraints according to the filter defined by user, using the drawConstraint function
		"""	
		involvedResidueslist = []
		numberOfDrawnConstraints = 0
		if len(aConstraintManager.constraints):
			start=time.clock()
			if aConstraintManager.associateToPDB():
				endAssociate=time.clock()
				for aConstraint in aConstraintManager.constraints:
					startFilter=time.clock()
					if aFilter.filter(aConstraint):
						endFilter=time.clock()
						if not aConstraint.resis[0]['number'] in involvedResidueslist:
							involvedResidueslist.append(aConstraint.resis[0]['number'])
						if not aConstraint.resis[1]['number'] in involvedResidueslist:
							involvedResidueslist.append(aConstraint.resis[1]['number'])
						if aConstraint.violated == 'violated':
							color = colors[aConstraint.constraintValues['closeness']]
						elif aConstraint.violated == 'not violated':
							color = colors['notViolated']
						drawConstraint(aConstraint.points, color, radius, aConstraint.getID())
						endDraw=time.clock()
						numberOfDrawnConstraints = numberOfDrawnConstraints + 1
						print "Filter;"+str(endFilter-startFilter)
						print "Draw;"+str(endDraw-endFilter)
				print "Association;"+str(endAssociate-start)
			return {'Residueslist':involvedResidueslist, 'DrawnConstraints':numberOfDrawnConstraints}
		else:
			stderr.write( "No constraints to draw ! You might want to load a few of them first ...\n")

	def constraintsDensity(self, aConstraintManager, aFilter):
		"""Calculate number of constraints per residue for selected constraints by the filter
		"""
		list = {}
		constraintsUsed = 0
		if len(aConstraintManager.constraints):
			if aConstraintManager.associateToPDB():
				for aConstraint in aConstraintManager.constraints:
					if aFilter.filter(aConstraint):
						if not aConstraint.resis[0]['number'] in list.keys():
							list[aConstraint.resis[0]['number']] = 10
						else:
							list[aConstraint.resis[0]['number']] = list[aConstraint.resis[0]['number']] + 10
						if not aConstraint.resis[1]['number'] in list.keys():
							list[aConstraint.resis[1]['number']] = 10
						else:
							list[aConstraint.resis[1]['number']] = list[aConstraint.resis[1]['number']] + 10
						constraintsUsed = constraintsUsed + 1
			stdout.write(str(constraintsUsed) + " used.\n")
			return list

	def paD(self, aConstraintManager, aFilter, color_gradient):
		"""Uses b-factors to simulate constraint density on structure
		"""
		densityList = self.constraintsDensity(aConstraintManager, aFilter)
		zeroBFactors(aConstraintManager.pdb)
		if len(densityList) > 0:
			for residu in densityList.keys():
				setBfactor(aConstraintManager.pdb + " & i. " + residu, densityList[residu])
		paintDensity(color_gradient, aConstraintManager.pdb)
		return densityList
