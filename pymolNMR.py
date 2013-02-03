from os import getcwd, chdir
from sys import stderr
#Needed to upload custom modules
installDir="/Users/olivier/Pymol_scripts/pyNMR/"
workingDir=getcwd()
chdir(installDir)

from NMRCLI import NMRCore
from NMRGUI import NMRGUI
chdir(workingDir)

#pymolNMR=NMRCore()

#try:
#	from pymol.cmd import extend
#	extend("loadNOE", pymolNMR.loadNOE)
#	extend("showNOE", pymolNMR.showNOE)
#	extend("showNOEDensity", pymolNMR.showNOEDensity)
#	extend("consStats", pymolNMR.consStats)
#	#cmd.extend("cnsToPDB", pymolNMR.cnsToPDB)
#	extend("loadAndShow", pymolNMR.loadAndShow)
#
#except ImportError:
#	stderr.write("Demo mode.\n")
	
class NMRApplication(object):
	def __init__(self):
		self.NMRCommands = NMRCore()		
		self.NMRInterface = NMRGUI()
		self.GUIBindings()
		
	def GUIBindings(self):
		self.NMRInterface.constraintFilesManagement.NMRCommands=self.NMRCommands
		self.NMRInterface.NOEDrawingManagement.NMRCommands=self.NMRCommands

if __name__=="__main__":
	application=NMRApplication()
	application.NMRInterface.mainloop()