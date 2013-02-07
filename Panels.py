from sys import stdout
from os import getcwd, chdir, path
import Tkinter as Tk
import Pmw
import tkFileDialog
from config import *

class Panel(Tk.LabelFrame):
	def __init__(self, master, frameText = ""):
		"""Abstract Class
		"""
		Tk.LabelFrame.__init__(self, master, text=frameText)
	
	def getInfo(self):
		return {}

class FileSelectionPanel(Panel):
	def __init__(self, master):
		Panel.__init__(self, master, frameText="Constraints Files")
		self.widgetCreation()
		self.NMRCommands=""#Must be set by application at run time
	
	def widgetCreation(self):
		self.constraintFilesButtonBox = Pmw.ButtonBox(self, labelpos = 'nw', orient='vertical')
		self.constraintFilesButtonBox.add("Load Constraints", command=self.loadFile)
		self.constraintFilesButtonBox.add("Remove Constraints", command=self.removeFile)
		self.constraintFilesButtonBox.grid(row=0, column=0)
		self.constraintsList=Pmw.ScrolledListBox(self)
		self.constraintsList.grid(row=0, column=1)
		self.constraintDefinitions = Pmw.RadioSelect(self, label_text="Select constraints definition type :",labelpos = 'nw', buttontype='radiobutton')
		self.constraintDefinitions.add("CNS/XPLOR")
		self.constraintDefinitions.add("CYANA/DYANA")
		self.constraintDefinitions.setvalue("CNS/XPLOR")
		self.constraintDefinitions.grid(row=1, column=0, columnspan=2)

	def loadFile(self):
		filename=tkFileDialog.askopenfilename(title="Open a constraint " + self.constraintDefinitions.getvalue() + " file ")
		constraintType=""
		if self.constraintDefinitions.getvalue()=="CNS/XPLOR":
			constraintDefinition="CNS"
		else:
			constraintDefinition="CYANA"
		self.NMRCommands.loadNOE(filename, constraintDefinition)
		self.constraintsList.setlist(self.NMRCommands.ManagersList.keys())
		self.constraintsList.setvalue(path.basename(filename))
	
	def removeFile(self):
		pass
	
	def getInfo(self):
		return {"constraintFile":self.constraintsList.getvalue()[0]}
		
class ConstraintSelectionPanel(Panel):
	def __init__(self, master):
		Panel.__init__(self, master, frameText="Constraints Selection")
		self.panelsList=[]
		self.widgetCreation()
	
	def widgetCreation(self):
		#Creation of range input
		self.consRangeFrame=RangeSelectionPanel(self)
		self.consRangeFrame.grid(row=0, column=0)
		self.panelsList.append(self.consRangeFrame)
	
		#Creation of Violations inputs
		self.violationsFrame=ViolationSelectionPanel(self)
		self.violationsFrame.grid(row=0, column=1)
		self.panelsList.append(self.violationsFrame)

		#Creation of structure inputs
		self.structureManagement = StructureSelectionPanel(self)
		self.structureManagement.grid(row=1, column=0, columnspan=2)
		self.panelsList.append(self.structureManagement)
	
	def getInfo(self):
		infos={}
		for panel in self.panelsList:
			infos.update(panel.getInfo())
		return infos
	
class StructureSelectionPanel(Panel):
	def __init__(self, master):
		Panel.__init__(self, master, frameText="Structure")
		self.residueRanges=Tk.StringVar(self)
		self.pdb=Tk.StringVar(self)
		self.widgetCreation()	
		
	def widgetCreation(self):
		Tk.Label(self, text='Name :').grid(row=0, column=0, sticky=Tk.W)
		self.entry_Pdb=Tk.Entry(self, textvariable=self.pdb)
		self.entry_Pdb.grid(row=0, column=1)

		Tk.Label(self, text='Residues ranges :').grid(row=1, column=0, sticky=Tk.W)		
		self.entry_res=Tk.Entry(self, textvariable=self.residueRanges)
		self.entry_res.grid(row=1, column=1)
		self.residueRanges.set('all')
	
	def getInfo(self):
		return {"pdb":self.pdb.get(), "ranges":self.residueRanges.get()}


class NOEDrawingPanel(Panel):
	def __init__(self, master):
		Panel.__init__(self, master, frameText="NOE Representation")
		self.widgetCreation()
		self.NMRCommands=""#Must be set by application at run time
		
	def widgetCreation(self):		
		self.drawingNOEButtonBox = Pmw.ButtonBox(self, orient='vertical')
		self.drawingNOEButtonBox.add('Sticks', command = self.showSticks)
		self.drawingNOEButtonBox.add('Density', command = self.showDensity)
		self.drawingNOEButtonBox.add('Clean NOEs')
		self.drawingNOEButtonBox.grid(row=0, column=0)
		self.drawingNOEButtonBox.setdefault('Sticks')
	
	def showSticks(self):
		infos= self.master.getInfo()
		infos["method"]= "sum6"
		infos["colors"]=defaultColors
		self.NMRCommands.commandsInterpretation(infos["pdb"], infos["constraintFile"], infos["ranges"], infos["residuesRange"], infos["violationState"], infos["cutOff"], infos["method"])
		self.NMRCommands.showSticks(infos["constraintFile"], infos["pdb"], infos["colors"], infos["radius"])

	def showDensity(self):
		infos=self.master.getInfo()
		infos["method"]= "sum6"
		infos["colors"]=defaultColors
		self.NMRCommands.commandsInterpretation(infos["pdb"], infos["constraintFile"], infos["ranges"], infos["residuesRange"], infos["violationState"], infos["cutOff"], infos["method"])
		self.NMRCommands.showNOEDensity(infos["constraintFile"], infos["pdb"], infos["colors"])
		
class RangeSelectionPanel(Panel):
	def __init__(self, master):
		Panel.__init__(self, master, frameText="Range Selection")

		self.RangesVars={}
		self.RangesCB={}
		self.RangesFunctions={}
		self.widgetCreation()
	
	def widgetCreation(self):
		rowPosition=0
		for consRange in ['intra', 'sequential', 'medium', 'long']:
			self.RangesVars[consRange]=Tk.IntVar(self)
			self.RangesCB[consRange]=Tk.Checkbutton(self, text=': ' + consRange, command=self.tick, variable=self.RangesVars[consRange])
			self.RangesCB[consRange].grid(row=rowPosition, column=0, sticky=Tk.W)
			rowPosition=rowPosition+1
		self.RangesVars["all"]=Tk.IntVar(self)
		self.RangesCB["all"]=Tk.Checkbutton(self, text=': all', command=self.tickAll, variable=self.RangesVars["all"])
		self.RangesCB["all"].grid(row=rowPosition, column=0, sticky=Tk.W)
		self.RangesCB["all"].invoke()

	def tickAll(self):
		if self.RangesVars["all"].get()==1:
			for consRange in ['intra', 'sequential', 'medium', 'long']:
				self.RangesCB[consRange].select()
		if self.RangesVars["all"].get()==0:
			for consRange in ['intra', 'sequential', 'medium', 'long']:
				self.RangesCB[consRange].deselect()
	def tick(self):
		self.RangesCB["all"].select()
		for aRange in ['intra', 'sequential', 'medium', 'long']:
			if self.RangesVars[aRange].get()==0:
				self.RangesCB["all"].deselect()
				break
	def getInfo(self):
		ranges=[]
		for consRange in ['intra', 'sequential', 'medium', 'long']:
			if self.RangesVars[consRange].get()==1:
				ranges.append(consRange)	
		return {"residuesRange":ranges}

class ViolationSelectionPanel(Panel):
	def __init__(self, master):
		Panel.__init__(self, master, frameText="Violation state Selection")

		self.ViolationsVars={}
		self.ViolatedCB={}
		self.cutOff=Tk.DoubleVar(self)
		self.widgetCreation()	
		
	def widgetCreation(self):
		rowPosition=0
		for violationType in ['violated', 'not violated']:
			self.ViolationsVars[violationType]=Tk.IntVar(self)
			self.ViolatedCB[violationType]=Tk.Checkbutton(self, text=': ' + violationType, variable=self.ViolationsVars[violationType])
			self.ViolatedCB[violationType].grid(row=rowPosition, column=0, sticky=Tk.W)
			self.ViolatedCB[violationType].select()
			rowPosition=rowPosition+1
		
		Tk.Label(self, text='Distance CutOff (A)').grid(row=rowPosition+1, column=0)
		
		self.spinBox_cutOff=Tk.Spinbox(self, textvariable=self.cutOff, from_=0.0, to=10.0, increment=0.1)
		self.cutOff.set('0.5')
		self.spinBox_cutOff.grid(row=rowPosition+2, column=0)
	
	def getInfo(self):
		violationState=[]		
		for violationType in ['violated','not violated']:
			if self.ViolationsVars[violationType].get()==1:
				violationState.append(violationType)
		return {"cutOff":self.cutOff.get(), "violationState":violationState}

class SticksPreferencesPanel(Panel):
	def __init__(self, master):
		Panel.__init__(self, master, frameText="NOE Sticks Preferences")
		self.radius=Tk.DoubleVar(self)
		self.radius.set(0.03)
		self.colors={"notViolated":"","tooFar":"", "tooClose":""}
		self.widgetCreation()
	
	def widgetCreation(self):
		Tk.Label(self, text='Stick radius (A):').grid(row=0, column=0)
		self.spinBox_Radius=Tk.Spinbox(self, textvariable=self.radius, from_=0.00, to=0.5, increment=0.01)
		self.spinBox_Radius.grid(row=0, column=1)

	
	def getInfo(self):
		return {"radius":self.radius.get()}

class DensityPreferencesPanel(Panel):
	def __init__(self, master):
		Panel.__init__(self, master, frameText="NOE density Preferences")
		self.gradient=Tk.StringVar(self)
		self.widgetCreation()

	def widgetCreation(self):
		Tk.Label(self, text='Gradient :').grid(row=0, column=0)

class PreferencesPanel(Panel):
	def __init__(self, master):
		Panel.__init__(self, master, frameText="NOE Preferences")
		self.method=Tk.StringVar(self)
		self.panelsList=[]
		self.widgetCreation()
	
	def widgetCreation(self):
		Tk.Label(self, text='NOE Distance calculation :\n(> 2 atoms)').grid(row=0, column=0)
		self.sticksPanel = SticksPreferencesPanel(self)
		self.sticksPanel.grid(row=1, column=0, columnspan=2)
		self.panelsList.append(self.sticksPanel)
		
		self.densityPanel = DensityPreferencesPanel(self)
		self.densityPanel.grid(row=2, column=0, columnspan=2)
		self.panelsList.append(self.densityPanel)
	
	def getInfo(self):
		infos={"method":self.method.get()}
		for panel in self.panelsList:
			infos.update(panel.getInfo())
		return infos