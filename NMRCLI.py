#!/usr/bin/env python

from sys import stderr
from os.path import exists
from os import getcwd, chdir
#Default Parameters
installDir="/Users/olivier/Pymol_scripts/pyNMR/"
workingDir=getcwd()
chdir(installDir)
from config import *
from NMRCore import NMRCore
chdir(workingDir)

NMRCommands=NMRCore()

def showNOE(pdb='', managerName="", residuesList='all', dist_range='all', violationState='all', violCutoff=defaultViolCutoff, method="sum6", radius=defaultRadius, colors=defaultColors):
	if managerName=='' and NMRCommands.ManagersList["defaultManager"]=="":
		stderr.write("No constraints loaded.\n")
	else:
		if managerName=='':
			managerName=NMRCommands.ManagersList["defaultManager"]
		if managerName in NMRCommands.ManagersList:
			NMRCommands.commandsInterpretation(pdb, managerName, residuesList, dist_range, violationState, violCutoff, method, colors, radius)
			NMRCommands.showSticks(managerName, pdb)
		else:
			stderr.write("Please check constraints filename.\n")

def loadNOE(filename="", consDef=""):
	"""load NMR distance constraints, call for the correct file format (CNS/CYANA),
	"""
	if exists(filename):
		NMRCommands.loadNOE(filename, consDef.upper())
	else:
		stderr.write("File : "+ filename +" has not been found.\n")
