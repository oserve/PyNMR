from sys import stdout
from os import getcwd, chdir, path
import Tkinter as Tk
import Pmw

installDir="/Users/olivier/Pymol_scripts/pyNMR/"
workingDir=getcwd()
chdir(installDir)

import Panels

chdir(workingDir)

class NMRGUI(Tk.Tk):
	def __init__ (self):
		Tk.Tk.__init__(self)
		self.title('PymolNMR')
		stdout.write( "Opening graphic interface ...\n")
		self.panelsList=[]
		self.createPanels()
		
	def createPanels(self):
		#Main Frames (not IBM)
		self.constraintSelectionManagement = Panels.ConstraintSelectionPanel(self)
		self.constraintSelectionManagement.grid(row=0, column=1)
		self.panelsList.append(self.constraintSelectionManagement)

		self.constraintFilesManagement = Panels.FileSelectionPanel(self)
		self.constraintFilesManagement.grid(row=0, column=0)
		self.panelsList.append(self.constraintFilesManagement)

		self.NOEDrawingManagement = Panels.NOEDrawingPanel(self)
		self.NOEDrawingManagement.grid(row=0, column=2)
		self.panelsList.append(self.NOEDrawingManagement)

	def getInfo(self):
		infos={}
		for panel in self.panelsList:
			infos.update(panel.getInfo())
		return infos
