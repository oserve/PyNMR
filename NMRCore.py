#NMRCore.py 08/2009 by Olivier Serve
#load CNS or DYANA distances constraints files
#into molecular viewer, display them on the molecule
#and show violated constraints according to a cutOff
#with different color (White for not violated, blue for lower limit violation, red for upper limit violation for NOEs)
#Required modules
from os.path import basename, exists
from sys import stderr, stdout
#Custom Class
from NOE import NOE
from ConstraintLoading import *
from Filtering import ConstraintFilter
from ConstraintsDrawing import ConstraintDrawer
from MolecularViewerInterface import select, zoom, delete

class NMRCore(object):
	
	def __init__(self):
		self.ManagersList={}
		self.filter=""
		self.displayedConstraints=[]

	def loadNOE(self, filename, consDef):
		"""load NMR distance constraints, call for the correct file format (CNS/CYANA),
		"""
		managerName=basename(filename)
		if consDef in ['XPLOR', 'CNS']:
			self.ManagersList[managerName]=cns(filename, managerName)
		elif consDef in ['DYANA', 'CYANA']:
			self.ManagersList[managerName]=dyana(filename,managerName)
		else:
			stderr.write("incorrect or unsupported constraint type.\n")
	
	def showSticks(self, managerName, pdb, colors, radius):
		self.ManagersList[managerName].setPDB(pdb)
		theFilter=self.filter
		drawer=ConstraintDrawer()
		selectedConstraints=[]
		if len(self.ManagersList[managerName].constraints):
			if self.ManagersList[managerName].associateToPDB():
				filteredConstraints=self.filter.filterConstraints(self.ManagersList[managerName].constraints)
				selectedConstraints=[]
				for constraint in filteredConstraints:
					if constraint not in self.displayedConstraints:
						selectedConstraints.append(constraint)
				self.displayedConstraints=self.displayedConstraints+selectedConstraints
				results=drawer.drC(selectedConstraints, radius, colors)
				stdout.write(str(results['DrawnConstraints'])+" constraints drawn on a total of "+str(len(self.ManagersList[managerName].constraints))+"\n")			
				zoomSelection=self.ManagersList[managerName].pdb+" &"
				if len(results['Residueslist']):
					for residue in results['Residueslist']:
						zoomSelection=zoomSelection+" resi "+residue+" +"
					zoom(zoomSelection.rstrip(' +'))
					select('involRes',zoomSelection.rstrip(' +'))
		else:
			stderr.write( "No constraints to draw ! You might want to load a few of them first ...\n")

	def showNOEDensity(self, managerName, pdb, gradient):
		"""Seeks for constraints that fit criteria, increases a counter for each residue which has a
		 matching constraint. That simulates a density which is then paint on the model according to a color gradient
		"""
		self.ManagersList[managerName].setPDB(pdb)
		theFilter=self.filter
		drawer=ConstraintDrawer()
		if len(self.ManagersList[managerName].constraints):
			if self.ManagersList[managerName].associateToPDB():
				selectedConstraints=theFilter.filterConstraints(self.ManagersList[managerName].constraints)
				self.displayedConstraints=self.displayedConstraints+selectedConstraints
				densityList=drawer.paD(selectedConstraints, self.ManagersList[managerName].pdb, gradient)
				zoomSelection=self.ManagersList[managerName].pdb+" &"
				if len(densityList):
					stdout.write(str(len(selectedConstraints)) + " constraints used.\n")
					stdout.write(str(len(densityList))+" residues involved.\n")
					for residue in densityList.keys():
						zoomSelection=zoomSelection+" resi "+residue+" +"
					zoom(zoomSelection.rstrip(' +'))
					select('involRes', zoomSelection.rstrip(' +'))
	
	def commandsInterpretation(self, pdb, managerName, residuesList, dist_range, violationState, violCutoff, method):
		"""Setup Filter for constraints
		"""
		if residuesList=='all':
			resList=self.ManagersList[managerName].residuesList
		else:
			resList=[]
			for resi_range in residuesList.split("+"):
				aRange=resi_range.split("-")
				if len(aRange)==2:
					for i in range(int(aRange[0]),int(aRange[1])+1):
						resList=resList+[str(i)]
				elif len(aRange)==1:
					resList=resList+[str(aRange)]
				else:
					stderr.write("Residues set definition error : "+residuesList+"\n")
		if type(dist_range)<>type([]):
			if dist_range=='all':
				dist_range=['intra', 'sequential', 'medium', 'long']
			else:
				dist_range=[dist_range]

		if type(violationState)<>type([]):
			if violationState=='all':
				violationState=['violated', 'not violated']
			else:
				violationState=[violationState]
		self.filter=ConstraintFilter(pdb, resList, dist_range, violationState, violCutoff, method)
	
	def cleanScreen(self, managerName):
		self.displayedConstraints=[]
		delete(managerName+"*")
