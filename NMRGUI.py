from sys import stdout
from os import getcwd, chdir, path
import Tkinter as Tk
import Pmw

from Panels import ConstraintSelectionPanel, FileSelectionPanel, NOEDrawingPanel, PreferencesPanel

class NMRGUI(Tk.Tk):
	def __init__ (self):
		Tk.Tk.__init__(self)
		self.title('PymolNMR')
		self.panelsList=[]
		self.createPanels()
		self.setDelegation()
		
	def createPanels(self):
		#Main Frames (not IBM)
		
		self.noteBook = Pmw.NoteBook(self)
		self.mainPage = self.noteBook.add("Main")
		
		self.constraintSelectionManagement = ConstraintSelectionPanel(self.mainPage)
		self.panelsList.append(self.constraintSelectionManagement)

		self.constraintFilesManagement = FileSelectionPanel(self.mainPage)
		self.panelsList.append(self.constraintFilesManagement)

		self.NOEDrawingManagement = NOEDrawingPanel(self.mainPage)
		self.panelsList.append(self.NOEDrawingManagement)

		self.preferencesPage = self.noteBook.add("Preferences")

		self.preferencesPanel= PreferencesPanel(self.preferencesPage)
		self.panelsList.append(self.preferencesPanel)
	
	def startGUI(self):
		self.noteBook.grid(row=0, column=0)
		self.constraintFilesManagement.grid(row=0, column=0)
		self.constraintSelectionManagement.grid(row=1, column=0)
		self.NOEDrawingManagement.grid(row=2, column=0)
		self.preferencesPanel.grid(row=0, column=0)		
		self.noteBook.setnaturalsize()

	def setDelegation(self):
		self.NOEDrawingManagement.mainApp=self
		
	def getInfo(self):
		infos={}
		for panel in self.panelsList:
			infos.update(panel.getInfo())
		return infos