from os import getcwd, chdir
from sys import stderr
#Needed to upload custom modules
installDir="/Users/olivier/Pymol_scripts/pyNMR/"
workingDir=getcwd()
chdir(installDir)
from config import *

from NMRCore import NMRCore
from NMRGUI import NMRGUI
chdir(workingDir)

Core=NMRCore()
	
class NMRApplication(object):
	def __init__(self, Core):
		self.NMRCommands = Core		
		self.NMRInterface = NMRGUI()
		self.log=""
		self.GUIBindings()
		
	def GUIBindings(self):
		self.NMRInterface.constraintFilesManagement.NMRCommands=self.NMRCommands
		self.NMRInterface.NOEDrawingManagement.NMRCommands=self.NMRCommands

pyNMR=NMRApplication(Core)

def showNOE(pdb='', managerName="", residuesList='all', dist_range='all', violationState='all', violCutoff=defaultViolCutoff, method="sum6", radius=defaultRadius, colors=defaultColors):
	if managerName=='' and Core.ManagersList["defaultManager"]=="":
		stderr.write("No constraints loaded.\n")
	else:
		if managerName=='':
			managerName=Core.ManagersList["defaultManager"]
		if managerName in Core.ManagersList:
			Core.commandsInterpretation(pdb, managerName, residuesList, dist_range, violationState, violCutoff, method)
			Core.showSticks(managerName, pdb, colors, radius)
		else:
			stderr.write("Please check constraints filename.\n")

def loadNOE(filename="", consDef=""):
	"""load NMR distance constraints, call for the correct file format (CNS/CYANA),
	"""
	if exists(filename):
		Core.loadNOE(filename, consDef.upper())
	else:
		stderr.write("File : "+ filename +" has not been found.\n")

def showNOEDensity(pdb='', managerName="", residuesList='all', dist_range='all', violationState='all', violCutoff=defaultViolCutoff, method='sum6', colors=defaultColors):
	if managerName=='' and Core.ManagersList["defaultManager"]=="":
		stderr.write("No constraints loaded.\n")
	else:
		if managerName=='':
			managerName=Core.ManagersList["defaultManager"]
		if managerName in Core.ManagersList:
			Core.commandsInterpretation(pdb, managerName, residuesList, dist_range, violationState, violCutoff, method)
			Core.showSticks(managerName, pdb, colors)
		else:
			stderr.write("Please check constraints filename.\n")

def loadAndShow(self, filename, consDef, pdb='',residuesList='all', dist_range='all', violationState='all', violCutoff=defaultViolCutoff, method="sum6", radius=defaultRadius, colors=defaultColors):
	"""
	"""
	loadNOE(filename, consDef)
	showNOE(pdb,filename, residuesList, dist_range, violationState, violCutoff, method, radius, colors)

if __name__=="__main__":
	pyNMR.NMRInterface.startGUI()
	pyNMR.NMRInterface.mainloop()
	
try:
	from pymol.cmd import extend
	extend("loadNOE", loadNOE)
	extend("showNOE", showNOE)
	extend("showNOEDensity", showNOEDensity)
	extend("loadAndShow", loadAndShow)

except ImportError:
	stderr.write("Demo mode.\n")
