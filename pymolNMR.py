# Copyright Notice
# ================
# 
# The PyMOL Plugin source code in this file is copyrighted, but you can
# freely use and copy it as long as you don't change or remove any of
# the copyright notices.
# 
# ----------------------------------------------------------------------
#               This PyMOL Plugin is Copyright (C) 2013 by 
#                 olivier serve <olivier dot serve at gmail dot com>
# 
#                        All Rights Reserved
# 
# Permission to use, copy, modify, distribute, and distribute modified
# versions of this software and its documentation for any purpose and
# without fee is hereby granted, provided that the above copyright
# notice appear in all copies and that both the copyright notice and
# this permission notice appear in supporting documentation, and that
# the name(s) of the author(s) not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
# 
# THE AUTHOR(S) DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS.  IN
# NO EVENT SHALL THE AUTHOR(S) BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
# USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
# ----------------------------------------------------------------------

from os import getcwd, chdir
from sys import stderr
from os.path import exists
#Needed to upload custom modules
installDir="/Users/olivier/Pymol_scripts/pyNMR/"
workingDir=getcwd()
chdir(installDir)

from NMRCore import NMRCore
from NMRGUI import NMRGUI
chdir(workingDir)

from pymol.cmd import get_names

Core=NMRCore()
	
class NMRApplication(object):
	def __init__(self, Core):
		self.NMRCommands = Core		
		self.log=""
		self.defaults={"radius":0.03, "cutOff":0.3, "colors":{'notViolated':[1,1,1,1,1,1],'tooFar':[1,0,0,1,0,0],'tooClose':[0,0,1,0,0,1]}, 'gradient':"blue_white_red"}

	def startGUI(self):
		self.NMRInterface = NMRGUI()
		self.NMRInterface.startGUI()
		self.GUIBindings()		
		self.setDefaults()
	
	def setDefaults(self):
		self.NMRInterface.preferencesPanel.densityPanel.gradientSelection.setlist( ["blue_green","blue_magenta","blue_red","blue_white_green","blue_white_magenta","blue_white_red","blue_white_yellow","blue_yellow","cbmr","cyan_magenta","cyan_red","cyan_white_magenta","cyan_white_red","cyan_white_yellow","cyan_yellow","gcbmry","green_blue","green_magenta","green_red","green_white_blue","green_white_magenta","green_white_red","green_white_yellow","green_yellow","green_yellow_red","magenta_blue","magenta_cyan","magenta_green","magenta_white_blue","magenta_white_cyan","magenta_white_green","magenta_white_yellow","magenta_yellow","rainbow","rainbow2","rainbow2_rev","rainbow_cycle","rainbow_cycle_rev","rainbow_rev red_blue","red_cyan red_green","red_white_blue","red_white_cyan","red_white_green","red_white_yellow","red_yellow","red_yellow_green","rmbc","yellow_blue","yellow_cyan","yellow_cyan_white","yellow_green","yellow_magenta","yellow_red","yellow_white_blue","yellow_white_green","yellow_white_magenta","yellow_white_red","yrmbcg"])
		self.NMRInterface.preferencesPanel.densityPanel.gradientSelection.component("entryfield").setvalue(self.defaults["gradient"])
		self.NMRInterface.preferencesPanel.sticksPanel.colors=self.defaults["colors"]
		self.NMRInterface.preferencesPanel.sticksPanel.radius.set(self.defaults["radius"])
		self.NMRInterface.constraintSelectionManagement.violationsFrame.cutOff.set(self.defaults["cutOff"])
		self.NMRInterface.constraintSelectionManagement.structureManagement.comboPDB.setlist(self.getModelsNames())
		self.NMRInterface.constraintFilesManagement.updateFilelist()

	def GUIBindings(self):
		self.NMRInterface.constraintFilesManagement.NMRCommands=self.NMRCommands
		self.NMRInterface.NOEDrawingManagement.NMRCommands=self.NMRCommands
		self.NMRInterface.constraintSelectionManagement.structureManagement.mainApp=self
	
	def getModelsNames(self):
		results=[]
		objectsLists=get_names()
		for name in objectsLists:
			if len(self.NMRCommands.ManagersList):
				for managerName in self.NMRCommands.ManagersList.keys():
					if name.find(managerName)<0:
						results.append(name)
			else:
				results.append(name)
		return results

pyNMR=NMRApplication(Core)

def showNOE(pdb='', managerName="", residuesList='all', dist_range='all', violationState='all', violCutoff=pyNMR.defaults["cutOff"], method="sum6", radius=pyNMR.defaults["radius"], colors=pyNMR.defaults["colors"]):
	if managerName=='' and len(Core.ManagersList)==0:
		stderr.write("No constraints loaded.\n")
	else:
		if managerName=='':
			managerName=Core.ManagersList.keys()[0]
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

def showNOEDensity(pdb='', managerName="", residuesList='all', dist_range='all', violationState='all', violCutoff=pyNMR.defaults["cutOff"], method='sum6', colors=pyNMR.defaults["gradient"]):
	if managerName=='' and len(Core.ManagersList)==0:
		stderr.write("No constraints loaded.\n")
	else:
		if managerName=='':
			managerName=Core.ManagersList.keys()[0]
		if managerName in Core.ManagersList:
			Core.commandsInterpretation(pdb, managerName, residuesList, dist_range, violationState, violCutoff, method)
			Core.showNOEDensity(managerName, pdb, colors)
		else:
			stderr.write("Please check constraints filename.\n")

def loadAndShow(filename, consDef, pdb='', residuesList='all', dist_range='all', violationState='all', violCutoff=pyNMR.defaults["cutOff"], method="sum6", radius=pyNMR.defaults["radius"], colors=pyNMR.defaults["colors"]):
	"""
	"""
	loadNOE(filename, consDef)
	showNOE(pdb,filename, residuesList, dist_range, violationState, violCutoff, method, radius, colors)

def cleanScreen(filename):
	if filename in Core.ManagersList:
		Core.cleanScreen(filename)

if __name__=="__main__":
	pyNMR.startGUI()
	pyNMR.NMRInterface.mainloop()
	
try:
	from pymol.cmd import extend
	extend("loadNOE", loadNOE)
	extend("showNOE", showNOE)
	extend("showNOEDensity", showNOEDensity)
	extend("loadAndShow", loadAndShow)

except ImportError:
	stderr.write("Demo mode.\n")
