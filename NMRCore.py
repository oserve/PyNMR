#NMRCore.py 08/2009 by Olivier Serve
#load CNS or DYANA distances constraints files
#into molecular viewer, display them on the molecule
#and show violated constraints according to a cutOff
#with different color (White for not violated, blue for lower limit violation, red for upper limit violation for NOEs)
#Required modules
from os.path import basename, exists
from sys import stderr, stdout

from NOE import NOE
from ConstraintLoading import *
from Filtering import ConstraintFilter
from ConstraintsDrawing import ConstraintDrawer
from MolecularViewerInterface import select, zoom

#Default Parameters
from config import *

#Miscellaneous definitions

class NMRCore(object):
	
	def __init__(self):
		self.ManagersList={}
		self.ManagersList["defaultManager"]=""
		self.filter=""
		self.displayParameters={}

	#CLI function definitions
	def loadNOE(self, filename, consDef):
		"""load NMR distance constraints, call for the correct file format (CNS/CYANA),
		"""
		managerName=basename(filename)
		if consDef in ['XPLOR', 'CNS']:
			self.ManagersList[managerName]=cns(filename, managerName)
			self.ManagersList["defaultManager"]=managerName 
		elif consDef in ['DYANA', 'CYANA']:
			self.ManagersList[managerName]=dyana(filename,managerName)
			self.ManagersList["defaultManager"]=managerName 
		else:
			stderr.write("incorrect or unsupported constraint type.\n")
	
	def showNOE(self, pdb='', managerName="", residuesList='all', dist_range='all', violationState='all', violCutoff=defaultViolCutoff, method="sum6", radius=defaultRadius, colors=defaultColors):
		"""Main function : seeks for NOE constraints that fit the criteria and draw them
		"""
		if managerName=='' and self.ManagersList["defaultManager"]=="":
			stderr.write("No constraints loaded.\n")		
		else:
			if managerName=='':
				managerName=self.ManagersList["defaultManager"]
			self.ManagersList[managerName].setPDB(pdb)
			theFilter=self.filterSetup(managerName, residuesList, dist_range, violationState, violCutoff, method)
			radius=float(radius)
			drawer=ConstraintDrawer()
			selectedConstraints=[]
			if len(self.ManagersList[managerName].constraints):
				if self.ManagersList[managerName].associateToPDB():
					selectedConstraints=theFilter.filterConstraints(self.ManagersList[managerName].constraints)
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

	def showSticks(self, managerName, pdb):
		self.ManagersList[managerName].setPDB(pdb)
		theFilter=self.filter
		drawer=ConstraintDrawer()
		selectedConstraints=[]
		if len(self.ManagersList[managerName].constraints):
			if self.ManagersList[managerName].associateToPDB():
				selectedConstraints=self.filter.filterConstraints(self.ManagersList[managerName].constraints)
				results=drawer.drC(selectedConstraints, self.displayParameters["radius"], self.displayParameters["colors"])
				stdout.write(str(results['DrawnConstraints'])+" constraints drawn on a total of "+str(len(self.ManagersList[managerName].constraints))+"\n")			
				zoomSelection=self.ManagersList[managerName].pdb+" &"
				if len(results['Residueslist']):
					for residue in results['Residueslist']:
						zoomSelection=zoomSelection+" resi "+residue+" +"
					zoom(zoomSelection.rstrip(' +'))
					select('involRes',zoomSelection.rstrip(' +'))
		else:
			stderr.write( "No constraints to draw ! You might want to load a few of them first ...\n")

	def showNOEDensity(self, pdb='', managerName="", residuesList='all', dist_range='all', violationState='all', violCutoff=defaultViolCutoff, method='sum6', colors=defaultColors):
		"""Seeks for constraints that fit criteria, increases a counter for each residue which has a
		 matching constraint. That simulates a density which is then paint on the model according to a color gradient
		"""
		if managerName=='' and self.ManagersList["defaultManager"]=="":
			stderr.write("No constraints loaded.\n")
		else:
			if managerName=='':
				managerName=self.ManagersList["defaultManager"]
			self.ManagersList[managerName].setPDB(pdb)
			theFilter=self.filterSetup(managerName, residuesList, dist_range, violationState, violCutoff, method)
			drawer=ConstraintDrawer()
			if len(self.ManagersList[managerName].constraints):
				if self.ManagersList[managerName].associateToPDB():
					selectedConstraints=theFilter.filterConstraints(self.ManagersList[managerName].constraints)
					densityList=drawer.paD(selectedConstraints, self.ManagersList[managerName].pdb, colors['gradient'])
					zoomSelection=self.ManagersList[managerName].pdb+" &"
					if len(densityList):
						stdout.write(str(len(selectedConstraints)) + " constraints used.\n")
						stdout.write(str(len(densityList))+" residues involved.\n")
						for residue in densityList.keys():
							zoomSelection=zoomSelection+" resi "+residue+" +"
						zoom(zoomSelection.rstrip(' +'))
						select('involRes', zoomSelection.rstrip(' +'))
	
	def commandsInterpretation(self, pdb, managerName, residuesList, dist_range, violationState, violCutoff, method, colors, radius):
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
		self.displayParameters["colors"]=colors
		self.displayParameters["radius"]=radius

	#def consStats(self, managerName='', pdb='', residuesList='all', dist_range='all', violationState='all', violCutoff=defaultViolCutoff):
	#	"""
	#	"""
	#	if managerName=='':
	#		stderr.write("No constraints loaded.\n")
	#	else:
	#		if pdb<>'':
	#			self.ManagersList[managerName].setPDB(pdb)
	#			filterSetup(managerName,residuesList, dist_range,violationState,violCutoff)	
	#	liste= self.ManagersList[managerName].residuesList
	#	for residu in liste:
	#		stdout.write( residu+"\n")
	
	def loadAndShow(self, filename, consDef, pdb='',residuesList='all', dist_range='all', violationState='all', violCutoff=defaultViolCutoff, method="sum6", radius=defaultRadius, colors=defaultColors):
		"""
		"""
		loadCons(filename, consDef)
		showNOE(filename, pdb, residuesList, dist_range, violationState, violCutoff, method, radius, colors)

	#def cnsToPDB(seqfile,manager=''):
	#	"""
	#	"""
	#	fin=open(seqfile,'r')
	#	resis_list=[]
	#	for resi in fin:
	#		resis_list.append(resi.lower())
	#	fin.close()
	#	resis_names={'arg':['HB','HG','HD'],'asn':['HB'],'asp':['HB'],'cys':['HB'],'gln':['HB','HG'],'glu':['HB','HG'],'gly':['HA'],'his':['HB'],'leu':['HB'],'lys':['HB','HG','HD','HE'],'met':['HB','HG'],'phe':['HB'],'pro':['HB','HG','HD'],'ser':['HB','HG'],'trp':['HB'],'tyr':['HB']}
	#	for aConstraint in ManagersList[manager].constraints:
	#		for resi_name in resis_names.keys():
	#			for position in ['init','final']:
	##										  print "testing position "+position
	##										  print "checking "+aConstraint.resis[position]['number']+" for "+resi_name
	##										  print "residu should be "+resis_list[int(aConstraint.resis[position]['number'])-1]
	#				if resis_list[int(aConstraint.resis[position]['number'])-1].find(resi_name)>-1:
	#					print "found "+resi_name
	#					if aConstraint.resis[position]['atoms'] in resis_names[resi_name]:
	#						if aConstraint.resis[position]['atoms_number']=='2':
	#							print "found 2"
	#							aConstraint.resis[position]['atoms_number']='3'
	#							if aConstraint.resis[position]['atoms_number']=='1':
	#								aConstraint.resis[position]['atoms_number']='2'
	#								print "found 3"
	#				if aConstraint.resis[position]['atoms']=='HN':
	#					print "found HN"
	#					aConstraint.resis[position]['atoms']='H'
	#	print len(resis_list)
	#	print resis_list[-1]