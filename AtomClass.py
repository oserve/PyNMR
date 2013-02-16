#  AtomClass.py
#  
#
#  Created by olivier on 16/05/09.
#  Copyright (c) 2009 ICSN. All rights reserved.
#
import re
from MolecularViewerInterface import select
lastDigit=re.compile('\d(\b|\Z)')#look for last digit of atom type (used in MyAtom)

class AtomSet(object):
	"""Base Class contains residu number
		and the atom type of the atom
	"""
	
	def __init__(self, pdbName,resi_number, resi_type):
		"""Initialisation sets the residu number
			and the atom type
		"""
		self.pdb=pdbName
		self.number=resi_number
		self.atType=resi_type
	
	def getID(self):
		"""return ID of the atom for selection
			by Pymol functions. Form : pdb & i. Number & n. atomType
			should be more independent from pymol, maybe should not be here at all ...
		"""			
		selection=self.pdb+" & i. "+str(self.number)+" & n. "+str(self.atType)
		if not select("",selection):# often due to different format (e.g. : HB2 -> 2HB)
			if self.atType=='HN':
				self.atType='H'
			elif self.atType=='H':
				self.atType='HN'
			elif lastDigit.search(self.atType):
				digit=lastDigit.search(self.atType).group()[0]
				self.atType=digit+lastDigit.sub('',self.atType)# put final digit at the beginning)
			self.atType='*'+self.atType
			selection=self.pdb+" & i. "+str(self.number)+" & n. "+str(self.atType)
			if not select("",selection):
				selection="noID"
		return selection
