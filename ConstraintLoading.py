#
#  ConsLoading.py
#
#
#  Created by olivier on 17/05/09.
#  Copyright (c) 2009 ICSN. All rights reserved.
#
#DistanceConstraints loading functions
from sys import stderr, stdout
import re

from NOE import NOE
from ConstraintManager import ConstraintSetManager


#Useful RegEx definitions
Par=re.compile('[()]')# used in cns constraints loading. Suppression of ()
SPar=re.compile("\(.*\)")#used in cns constraint loading.
RegResi=re.compile("resi\w*\s+\d+\s+and\s+name\s+\w\w?\d*[\*#]*")#match CNS Residue definition
Sharp=re.compile('[#]')# used in cns constraints loading. Replace # by *
AtType=re.compile('[chon][a-z]*')

def cns(cnsFile, managerName):
	"""
	Return a ConstraintSetManager loaded with cns/xplor constraints
	"""
	fin=open(cnsFile,'r')
	#Avoid formatting issues
	inFileTab=[]
	for txt in fin:
		txt=txt.lstrip()
		if txt.find('!')<0:
			inFileTab.append(txt.lower().rstrip())
		else:
			stderr.write(txt+" skipped. Commented out.\n")
	fin.close()
	validCNSConstraints=[]
	for line in inFileTab:
		if line.find("assi")>-1:
			line=line.replace("gn", "")
			validCNSConstraints.append(line.replace("assi",""))
		elif RegResi.search(line)<>None:
			validCNSConstraints[-1]=validCNSConstraints[-1]+line

	constraint_number=1
	aManager=ConstraintSetManager(managerName)
	for aConstLine in validCNSConstraints:#itemizing constraints
		#avoid empty lines
		if re.search('\d', aConstLine):
			parsingResult = parseCNSConstraint(aConstLine)
			if len(parsingResult)==3:#2 residues + distances (matches also H-Bonds)
				aConstraint=NOE()
			else:
				#No other constraint type supported ... for now !
				break
			aConstraint.id["number"]=constraint_number
			aConstraint.definition=aConstLine
			for position in range(aConstraint.numberOfAtomsSets):
				currentResidue={}
				if  "resid" in parsingResult[position].keys():
					currentResidue["number"]=parsingResult[position]["resid"]
				else:
					currentResidue["number"]=parsingResult[position]["resi"]						
				currentResidue["atoms"]=AtType.match(parsingResult[position]["name"]).group()
				currentResidue["atoms_number"]=AtType.sub('', parsingResult[position]["name"])
				currentResidue["ambiguity"]=AtType.sub('', parsingResult[position]["name"]).find('*')
				if "segid" in parsingResult[position].keys():
					currentResidue["segid"]=parsingResult[position]["segid"]
				aConstraint.resis.append(currentResidue)
			aConstraint.setConstraintValues(parsingResult[-1][0],parsingResult[-1][1],parsingResult[-1][2])#Values always at the end of the array
			
			aManager.addConstraint(aConstraint)
			constraint_number=constraint_number+1
		else:
			stderr.write("This line : "+aConstLine+" is not a valid constraint.\n")
			continue
	stdout.write(str(len(aManager.constraints))+" constraints loaded.\n")
	return aManager

def convertTypeDyana(atType):
	"""
	Adapt xeasy nomenclature Q to pymol *
	"""
	if atType.count('Q'):
		newType=atType.replace('Q','H',1)
		newType=newType+('*') # Q is replaced by H and a star at the end of the atom type
		newType=newType.replace('Q','')# avoid QQ (QQD-> HD*)
		return newType
	else:
		return atType


def dyana(dyanaFile,managerName):
	""""
	Return a ConstraintSetManager loaded with CYANA/DYANA constraints
	"""
	fin=open(dyanaFile,'r')
	i=1
	aManager=ConstraintSetManager(managerName)
	for aConstLine in fin:
		if len(aConstLine)>1:
			if aConstLine.lstrip().find('#')==0:
				stderr.write(aConstLine+" skipped. Commented out.\n")
			else:
				cons_tab=aConstLine.split()
				try: #For errors not filtered previously
					aConstraint=NOE.initWith(i, cons_tab[0], AtType.match(convertTypeDyana(cons_tab[2])).group(),AtType.sub('',convertTypeDyana(cons_tab[2])) ,cons_tab[3], AtType.match(convertTypeDyana(cons_tab[5])).group(), AtType.sub('',convertTypeDyana(cons_tab[5])), aConstLine)
					aConstraint.setConstraintValues(str(1.8+(float(cons_tab[6])-1.8)/2),'1.8',cons_tab[6])
					aManager.addConstraint(aConstraint)
					i=i+1
				except:
					stderr.write("Unknown error while loading constraint :\n"+aConstLine+"\n")
		else:
			stderr.write("Empty line, skipping.\n")

	fin.close()
	stdout.write(str(len(aManager.constraints))+" constraints loaded.\n")
	return aManager

def parseCNSConstraint(aCNSConstraint):
	"""Split CNS/XPLOR type constraint into an array, contening the name of the residues (as arrays),
	and the values of the parameter associated to the constraint. It should be independant
	from the type of constraint (dihedral, distance, ...)
	"""
	residuesList=RegResi.findall(aCNSConstraint, re.IGNORECASE)
	constraintValuesList=SPar.sub("", aCNSConstraint).split()
	constraintParsingResult=[]
	for aResidue in residuesList:
		residueParsingResult={}
		for aDefinition in Sharp.sub('*', aResidue).split("and"):
			definitionArray=aDefinition.split()
			residueParsingResult[definitionArray[0].strip()]=definitionArray[1].strip()
		constraintParsingResult.append(residueParsingResult)
	numericValues=[]
	for aValue in constraintValuesList:
		numericValues.append(float(aValue))
	constraintParsingResult.append(numericValues)
	return constraintParsingResult