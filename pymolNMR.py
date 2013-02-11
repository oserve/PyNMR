from os import getcwd, chdir
from sys import stderr
#Needed to upload custom modules
installDir="/Users/olivier/Pymol_scripts/pyNMR/"
workingDir=getcwd()
chdir(installDir)

defaultRadius=0.03 # Angstrom
defaultViolCutoff=0.3 # Angstrom
defaultColors={'notViolated':[1,1,1,1,1,1],'tooFar':[1,0,0,1,0,0],'tooClose':[0,0,1,0,0,1],'gradient':"blue_white_red"}
defaultRGBColors={'notViolated':[1,1,1],'tooFar':[1,0,0],'tooClose':[0,0,1],'gradient':"blue_white_red"}

from NMRCore import NMRCore
from NMRGUI import NMRGUI
chdir(workingDir)

Core=NMRCore()
	
class NMRApplication(object):
	def __init__(self, Core):
		self.NMRCommands = Core		
		self.NMRInterface = NMRGUI()
		self.log=""
		self.defaults={"radius":0.03, "cutOff":0.3, "colors":{'notViolated':[1,1,1,1,1,1],'tooFar':[1,0,0,1,0,0],'tooClose':[0,0,1,0,0,1],'gradient':"blue_white_red"}}
		self.NMRInterface.preferencesPanel.sticksPanel.colors=self.defaults["colors"]
		self.NMRInterface.preferencesPanel.sticksPanel.radius.set(self.defaults["radius"])
		self.NMRInterface.constraintSelectionManagement.violationsFrame.cutOff.set(self.defaults["cutOff"])
		self.GUIBindings()
		
	def GUIBindings(self):
		self.NMRInterface.constraintFilesManagement.NMRCommands=self.NMRCommands
		self.NMRInterface.NOEDrawingManagement.NMRCommands=self.NMRCommands

pyNMR=NMRApplication(Core)

def showNOE(pdb='', managerName="", residuesList='all', dist_range='all', violationState='all', violCutoff=defaultViolCutoff, method="sum6", radius=pyNMR.defaults["radius"], colors=pyNMR.defaults["colors"]):
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

def showNOEDensity(pdb='', managerName="", residuesList='all', dist_range='all', violationState='all', violCutoff=defaultViolCutoff, method='sum6', colors=pyNMR.defaults["colors"]):
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

def loadAndShow(self, filename, consDef, pdb='',residuesList='all', dist_range='all', violationState='all', violCutoff=defaultViolCutoff, method="sum6", radius=defaultRadius, colors=pyNMR.defaults["colors"]):
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
